import json
from dataclasses import dataclass
from typing import List, Optional

import eave.core.internal.database as eave_db
import eave.core.internal.orm as eave_orm
import eave.stdlib.util as eave_util
import fastapi
import requests_oauthlib
from eave.core.internal.config import app_config

from . import oauth_cookie, oauth_state


@dataclass
class AtlassianOAuthTokenResponse:
    access_token: str
    expires_in: int
    scope: str


@dataclass
class AtlassianAvailableResource:
    """
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/#implementing-oauth-2-0--3lo-
    """

    id: str
    name: str
    url: str
    scopes: List[str]
    avatarUrl: str


async def atlassian_oauth_authorize() -> fastapi.Response:
    oauth_flow_info = get_oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=oauth_flow_info.authorization_url)
    oauth_cookie.save_state_cookie(
        response=response,
        state=oauth_flow_info.state,
        provider=eave_orm.AuthProvider.atlassian,
    )
    return response


async def atlassian_oauth_callback(
    state: str, code: str, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    expected_oauth_state = oauth_cookie.get_state_cookie(request=request, provider=eave_orm.AuthProvider.atlassian)
    assert state == expected_oauth_state

    oauth_session = build_oauth_session(state=expected_oauth_state)
    oauth_session.fetch_token(
        token_url="https://auth.atlassian.com/oauth/token",
        code=code,
        client_secret=app_config.eave_atlassian_app_client_secret,
    )

    available_resources_response = oauth_session.request(
        method="GET",
        url="https://api.atlassian.com/oauth/token/accessible-resources",
    )
    available_resources_data: List[eave_util.JsonObject] = available_resources_response.json()
    available_resources = [AtlassianAvailableResource(**j) for j in available_resources_data]
    assert len(available_resources) > 0
    atlassian_cloud_id = available_resources[0].id

    async with eave_db.get_async_session() as session:
        installation = await eave_orm.AtlassianInstallationOrm.one_or_none_by_atlassian_cloud_id(
            session=session,
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
        session.add(installation)
        await session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")
    oauth_cookie.delete_state_cookie(response=response, provider=eave_orm.AuthProvider.atlassian)
    return response


def build_oauth_session(state: Optional[str] = None) -> requests_oauthlib.OAuth2Session:
    session = requests_oauthlib.OAuth2Session(
        client_id=app_config.eave_atlassian_app_client_id,
        redirect_uri=f"{app_config.eave_api_base}/oauth/atlassian/callback",
        scope=" ".join(eave_orm.AtlassianInstallationOrm.oauth_scopes),
        state=state,
    )

    return session


def get_oauth_flow_info() -> oauth_state.OauthFlowInfo:
    session = build_oauth_session()

    authorization_url, state = session.authorization_url(
        url="https://auth.atlassian.com/authorize", audience="api.atlassian.com", prompt="consent"
    )

    assert isinstance(authorization_url, str)
    assert isinstance(state, str)
    return oauth_state.OauthFlowInfo(authorization_url=authorization_url, state=state)
