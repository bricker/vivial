from typing import cast

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.google
import eave.stdlib.auth_cookies as eave_auth_cookies
import eave.stdlib.core_api.enums
import fastapi
import google.oauth2.credentials
import google.oauth2.id_token
from eave.core.internal.config import app_config
from eave.core.internal.oauth import state_cookies as oauth_cookies
from eave.core.internal.orm.account import AccountOrm
from eave.core.internal.orm.team import TeamOrm


async def google_oauth_authorize() -> fastapi.Response:
    oauth_flow_info = eave.core.internal.oauth.google.get_oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=oauth_flow_info.authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=oauth_flow_info.state,
        provider=eave.stdlib.core_api.enums.AuthProvider.google,
    )
    return response


async def google_oauth_callback(state: str, code: str, request: fastapi.Request) -> fastapi.Response:
    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")

    expected_oauth_state = oauth_cookies.get_state_cookie(
        request=request, provider=eave.stdlib.core_api.enums.AuthProvider.google
    )
    oauth_cookies.delete_state_cookie(response=response, provider=eave.stdlib.core_api.enums.AuthProvider.google)
    assert state == expected_oauth_state

    flow = eave.core.internal.oauth.google.build_flow(state=state)
    flow.fetch_token(code=code)

    # flow.credentials returns a `google.auth.credentials.Credentials`, which is the base class of
    # google.oauth2.credentials.Credentials and doesn't contain common oauth properties like refresh_token.
    # The `cast` here gives us type hints, autocomplete, etc. for `flow.credentials`
    credentials = cast(google.oauth2.credentials.Credentials, flow.credentials)
    assert credentials.id_token is not None
    google_token = eave.core.internal.oauth.google.decode_id_token(id_token=credentials.id_token)

    auth_cookies = eave_auth_cookies.get_auth_cookies(cookies=request.cookies)

    if auth_cookies.access_token and auth_cookies.account_id:
        async with eave_db.async_session.begin() as db_session:
            eave_account = await AccountOrm.one_or_exception(
                session=db_session,
                id=auth_cookies.account_id,
                access_token=auth_cookies.access_token
            )

            if eave_account.auth_provider == eave.stdlib.core_api.enums.AuthProvider.google:
                # If the user is logged in through Slack, then take this opportunity to update the access and refresh tokens.
                if credentials.token:
                    eave_account.access_token = credentials.token

                if credentials.refresh_token:
                    eave_account.refresh_token = credentials.refresh_token

    else:
        eave_account = await _get_or_create_eave_account(google_token=google_token, credentials=credentials)

    # Set the cookie in the response headers.
    # This logs the user into their Eave account.
    eave_auth_cookies.set_auth_cookies(
        response=response,
        account_id=eave_account.id,
        access_token=eave_account.access_token,
    )

    return response


async def _get_or_create_eave_account(
    google_token: eave.core.internal.oauth.google.GoogleIdToken,
    credentials: google.oauth2.credentials.Credentials,
) -> AccountOrm:
    async with eave_db.async_session.begin() as db_session:
        # Check if an Eave Account already exists for this user ID.
        eave_account = await AccountOrm.one_or_none(
            session=db_session,
            auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
            auth_id=google_token.sub,
        )

        if eave_account is not None:
            if credentials.token:
                eave_account.access_token = credentials.token
            if credentials.refresh_token:
                eave_account.refresh_token = credentials.refresh_token

        else:
            beta_whitelisted = False  # Default value

            # No Eave account exists. Create one, along with a Team.
            if google_token.email:
                beta_prewhitelist = app_config.eave_beta_prewhitelisted_emails
                beta_whitelisted = google_token.email in beta_prewhitelist

            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team_name = f"{google_token.given_name}'s Team" if google_token.given_name else "Your Team"

            team = await TeamOrm.create(
                session=db_session,
                name=team_name,
                document_platform=None,
                beta_whitelisted=beta_whitelisted,
            )

            eave_account = await AccountOrm.create(
                session=db_session,
                team_id=team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
                auth_id=google_token.sub,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
            )

    return eave_account
