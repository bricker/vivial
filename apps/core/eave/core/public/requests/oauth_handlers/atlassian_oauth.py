import json

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.atlassian as oauth_atlassian
import eave.core.internal.oauth.cookies as oauth_cookies
import eave.stdlib.core_api.models as eave_models
import eave.core.internal.orm as eave_orm
import fastapi
from eave.core.internal.config import app_config


async def atlassian_oauth_authorize() -> fastapi.Response:
    oauth_session = oauth_atlassian.AtlassianOAuthSession()
    flow_info = oauth_session.oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=flow_info.authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=flow_info.state,
        provider=eave_models.AuthProvider.atlassian,
    )
    return response


async def atlassian_oauth_callback(
    state: str, code: str, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    expected_oauth_state = oauth_cookies.get_state_cookie(request=request, provider=eave_models.AuthProvider.atlassian)
    assert state == expected_oauth_state

    oauth_session = oauth_atlassian.AtlassianOAuthSession(state=state)
    oauth_session.fetch_token(code=code)
    atlassian_cloud_id = oauth_session.get_atlassian_cloud_id()

    async with eave_db.get_async_session() as db_session:
        installation = await eave_orm.AtlassianInstallationOrm.one_or_none(
            session=db_session,
            atlassian_cloud_id=atlassian_cloud_id,
        )
        # TODO: If the installation exists, that means that a team already connected this Atlassian account.
        # We should show an error to the user.
        assert installation is None

        installation = eave_orm.AtlassianInstallationOrm(
            team_id="e15a5cf3-004a-49df-b2f3-accf03eb4987",  # TODO: Get team ID from session.
            atlassian_cloud_id=atlassian_cloud_id,
            oauth_token_encoded=json.dumps(oauth_session.token),
        )
        db_session.add(installation)
        await db_session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")
    oauth_cookies.delete_state_cookie(response=response, provider=eave_models.AuthProvider.atlassian)
    return response
