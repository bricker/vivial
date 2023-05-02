import json

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.state_cookies as oauth_cookies
import eave.stdlib.core_api.enums as eave_enums
import eave.stdlib.auth_cookies
import fastapi
from eave.core.internal.config import app_config
from eave.core.internal.orm.atlassian_installation import AtlassianInstallationOrm
from eave.core.internal.orm.team import TeamOrm
from eave.core.internal.orm.account import AccountOrm
from eave.stdlib import logger

async def atlassian_oauth_authorize(request: fastapi.Request) -> fastapi.Response:
    auth_cookies = eave.stdlib.auth_cookies.get_auth_cookies(cookies=request.cookies)
    if not (auth_cookies.access_token and auth_cookies.account_id):
        logger.warning("Attempt to initiate Atlassian oauth while not logged in.")
        return fastapi.responses.RedirectResponse(url=app_config.eave_www_base)

    oauth_session = oauth_atlassian.AtlassianOAuthSession()
    flow_info = oauth_session.oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=flow_info.authorization_url)

    oauth_cookies.save_state_cookie(
        response=response,
        state=flow_info.state,
        provider=eave_enums.AuthProvider.atlassian,
    )
    return response


async def atlassian_oauth_callback(
    state: str,
    code: str,
    request: fastapi.Request,
) -> fastapi.Response:
    auth_cookies = eave.stdlib.auth_cookies.get_auth_cookies(cookies=request.cookies)
    if not (auth_cookies.access_token and auth_cookies.account_id):
        logger.warning("Attempt to complete Atlassian oauth while not logged in.")
        return fastapi.responses.RedirectResponse(url=app_config.eave_www_base)

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")

    expected_oauth_state = oauth_cookies.get_state_cookie(request=request, provider=eave_enums.AuthProvider.atlassian)
    oauth_cookies.delete_state_cookie(response=response, provider=eave_enums.AuthProvider.atlassian)
    assert state == expected_oauth_state

    oauth_session = oauth_atlassian.AtlassianOAuthSession(state=state)
    oauth_session.fetch_token(code=code)
    atlassian_cloud_id = oauth_session.get_atlassian_cloud_id()

    async with eave_db.async_session.begin() as db_session:
        # For Atlassian, we assume they are already logged in.
        eave_account = await AccountOrm.one_or_exception(
            session=db_session,
            id=auth_cookies.account_id,
            access_token=auth_cookies.access_token,
        )

        eave_team = await TeamOrm.one_or_exception(
            session=db_session,
            team_id=eave_account.team_id,
        )

        installation = await AtlassianInstallationOrm.one_or_none(
            session=db_session,
            team_id=eave_team.id,
        )

        if installation is None:
            installation = await AtlassianInstallationOrm.create(
                session=db_session,
                team_id=eave_team.id,
                atlassian_cloud_id=atlassian_cloud_id,
                oauth_token_encoded=json.dumps(oauth_session.token),
                confluence_space=None,
            )

    return response
