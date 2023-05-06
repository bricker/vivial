import typing
from typing import cast

import eave.core.internal.oauth.google
import eave.core.public.requests.util
import eave.stdlib.core_api.enums
import fastapi
import google.oauth2.credentials
import google.oauth2.id_token
from eave.core.internal.oauth import state_cookies as oauth_cookies

from . import shared

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.google


async def google_oauth_authorize() -> fastapi.Response:
    oauth_flow_info = eave.core.internal.oauth.google.get_oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=oauth_flow_info.authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=oauth_flow_info.state,
        provider=_AUTH_PROVIDER,
    )
    return response


async def google_oauth_callback(
    request: fastapi.Request,
    response: fastapi.Response,
    state: str,
    code: typing.Optional[str] = None,
    error: typing.Optional[str] = None,
    error_description: typing.Optional[str] = None,
) -> fastapi.Response:
    shared.verify_oauth_state_or_exception(
        state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response
    )

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    if error or not code:
        eave.stdlib.logger.warning(
            f"Error response from Google OAuth flow or code missing. {error}: {error_description}",
            extra=eave_state.log_context,
        )
        shared.set_redirect(response=response, location=eave.core.internal.app_config.eave_www_base)
        return response

    flow = eave.core.internal.oauth.google.build_flow(state=state)
    flow.fetch_token(code=code)

    # flow.credentials returns a `google.auth.credentials.Credentials`, which is the base class of
    # google.oauth2.credentials.Credentials and doesn't contain common oauth properties like refresh_token.
    # The `cast` here gives us type hints, autocomplete, etc. for `flow.credentials`
    credentials = cast(google.oauth2.credentials.Credentials, flow.credentials)
    assert credentials.id_token is not None

    google_token = eave.core.internal.oauth.google.decode_id_token(id_token=credentials.id_token)
    eave_team_name = f"{google_token.given_name}'s Team" if google_token.given_name else "Your Team"

    await shared.get_or_create_eave_account(
        request=request,
        response=response,
        eave_team_name=eave_team_name,
        user_email=google_token.email,
        auth_provider=_AUTH_PROVIDER,
        auth_id=google_token.sub,
        access_token=credentials.token,
        refresh_token=credentials.refresh_token,
    )

    return response
