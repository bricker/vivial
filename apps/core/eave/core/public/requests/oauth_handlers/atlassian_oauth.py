import json
import typing

from oauthlib.oauth2 import OAuth2Token

import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.state_cookies as oauth_cookies
import eave.stdlib
import eave.stdlib.core_api
import eave.core.internal
import eave.core.internal.orm
import fastapi
from eave.stdlib import logger
import eave.core.public.requests.util
from . import shared
import atlassian

_AUTH_PROVIDER = eave.stdlib.core_api.enums.AuthProvider.atlassian

async def atlassian_oauth_authorize(request: fastapi.Request) -> fastapi.Response:
    oauth_session = oauth_atlassian.AtlassianOAuthSession()
    flow_info = oauth_session.oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=flow_info.authorization_url)

    oauth_cookies.save_state_cookie(
        response=response,
        state=flow_info.state,
        provider=_AUTH_PROVIDER,
    )
    return response


async def atlassian_oauth_callback(
    state: str,
    code: str,
    request: fastapi.Request,
    response: fastapi.Response,
) -> fastapi.Response:
    shared.verify_oauth_state_or_exception(state=state, auth_provider=_AUTH_PROVIDER, request=request, response=response)

    eave_state = eave.core.public.requests.util.get_eave_state(request=request)

    oauth_session = oauth_atlassian.AtlassianOAuthSession(state=state)
    oauth_session.fetch_token(code=code)
    atlassian_cloud_id = oauth_session.atlassian_cloud_id

    token = typing.cast(OAuth2Token, oauth_session.token)
    access_token = token.get("access_token")
    refresh_token = token.get("refresh_token")

    if not access_token or not refresh_token:
        eave.stdlib.logger.warning("missing tokens.", extra=eave_state.log_context)
        raise eave.stdlib.exceptions.InvalidAuthError()

    userinfo = oauth_session.get_userinfo()
    if not userinfo.account_id:
        eave.stdlib.logger.warning("atlassian account_id missing; can't create account.", extra=eave_state.log_context)
        raise eave.stdlib.exceptions.InvalidAuthError()

    resources = oauth_session.get_available_resources()
    resource = next(iter(resources), None)

    if resource:
        eave_team_name = resource.name
    else:
        name = userinfo.display_name
        eave_team_name = f"{name}'s Team" if name else "Your Team"

    eave_account = await shared.get_or_create_eave_account(
        request=request,
        response=response,
        eave_team_name=eave_team_name,
        user_email=userinfo.email,
        auth_provider=_AUTH_PROVIDER,
        auth_id=userinfo.account_id,
        access_token=access_token,
        refresh_token=refresh_token,
    )

    await _update_or_create_installation(
        eave_state=eave_state,
        eave_account=eave_account,
        atlassian_cloud_id=atlassian_cloud_id,
        oauth_session=oauth_session,
    )

    return response

async def _update_or_create_installation(eave_state: eave.core.public.requests.util.EaveRequestState, eave_account: eave.core.internal.orm.AccountOrm, atlassian_cloud_id: str, oauth_session: oauth_atlassian.AtlassianOAuthSession) -> None:
    oauth_token_encoded = json.dumps(oauth_session.token)

    async with eave.core.internal.database.async_session.begin() as db_session:
        installation = await eave.core.internal.orm.AtlassianInstallationOrm.one_or_none(
            session=db_session,
            atlassian_cloud_id=atlassian_cloud_id,
        )

        if installation and installation.team_id != eave_account.team_id:
            msg = f"An Atlassian integration already exists for atlassian_cloud_id {atlassian_cloud_id}"
            await eave_state.add_note(msg)
            logger.warning(msg, extra=eave_state.log_context)
            return

        if installation and oauth_token_encoded:
            installation.oauth_token_encoded = oauth_token_encoded

        else:
            default_space_key = None

            try:
                # If the confluence site only has one global space, then use it.
                confluence_client = atlassian.Confluence(
                    url=oauth_session.api_base_url,
                    session=oauth_session,
                )

                spaces_response = confluence_client.get_all_spaces(space_status="current", space_type="global")
                spaces_response_json = typing.cast(eave.stdlib.util.JsonObject, spaces_response)
                spaces = [eave.stdlib.atlassian.ConfluenceSpace(s, oauth_session.confluence_context) for s in spaces_response_json["results"]]
                if len(spaces) == 1 and (first_space := next(iter(spaces), None)):
                    default_space_key = first_space.key

            except Exception as e:
                # We aggressively catch any error because this space fetching procedure is a convenience, but failure shouldn't prevent sign-up.
                eave.stdlib.logger.error("error while fetching confluence spaces", exc_info=e, extra=eave_state.log_context)

            installation = await eave.core.internal.orm.AtlassianInstallationOrm.create(
                session=db_session,
                team_id=eave_account.team_id,
                atlassian_cloud_id=atlassian_cloud_id,
                oauth_token_encoded=oauth_token_encoded,
                confluence_space_key=default_space_key,
            )