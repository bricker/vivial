from dataclasses import dataclass
from typing import Optional, cast

import eave.core.internal.database as eave_db
import eave.core.internal.oauth.models as oauth_models
import eave.core.internal.orm as eave_orm
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.util as eave_util
import fastapi
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import pydantic
from eave.core.internal.config import app_config
from eave.core.internal.oauth import cookies as oauth_cookies
from google.auth.transport import requests


async def google_oauth_authorize() -> fastapi.Response:
    oauth_flow_info = get_oauth_flow_info()
    response = fastapi.responses.RedirectResponse(url=oauth_flow_info.authorization_url)
    oauth_cookies.save_state_cookie(
        response=response,
        state=oauth_flow_info.state,
        provider=eave.stdlib.core_api.enums.AuthProvider.google,
    )
    return response


@dataclass
class GoogleOAuthResponseBody(pydantic.BaseModel):
    sub: str
    """Google globally unique and immutable user ID"""

    given_name: Optional[str]


async def google_oauth_callback(
    state: str, code: str, request: fastapi.Request, response: fastapi.Response
) -> fastapi.Response:
    expected_oauth_state = oauth_cookies.get_state_cookie(
        request=request, provider=eave.stdlib.core_api.enums.AuthProvider.google
    )
    assert state == expected_oauth_state

    flow = build_flow(state=state)
    flow.fetch_token(code=code)

    # flow.credentials returns a `google.auth.credentials.Credentials`, which is the base class of
    # google.oauth2.credentials.Credentials and doesn't contain common oauth properties like refresh_token.
    # The `cast` here gives us type hints, autocomplete, etc. for `flow.credentials`
    credentials = cast(google.oauth2.credentials.Credentials, flow.credentials)
    assert credentials.id_token is not None
    token = decode_id_token(id_token=credentials.id_token)

    userid = token.sub
    given_name = token.given_name
    async with eave_db.get_async_session() as session:
        account_orm = await eave_orm.AccountOrm.one_or_none(
            session=session,
            auth_info=eave_models.AuthInfo(
                provider=eave.stdlib.core_api.enums.AuthProvider.google,
                id=userid,
            ),
        )

        if account_orm is None:
            # If this is a new account, then also create a new team.
            # The Team is what is used for integrations, not an individual account.
            team = eave_orm.TeamOrm(
                name=f"{given_name}'s Team" if given_name is not None else "Your Team",
                document_platform=None,
            )

            session.add(team)
            await session.commit()

            account_orm = eave_orm.AccountOrm(
                team_id=team.id,
                auth_provider=eave.stdlib.core_api.enums.AuthProvider.google,
                auth_id=userid,
                oauth_token=credentials.id_token,
            )

            session.add(account_orm)

        account_orm.oauth_token = credentials.id_token
        await session.commit()

    response = fastapi.responses.RedirectResponse(url=f"{app_config.eave_www_base}/dashboard")
    oauth_cookies.delete_state_cookie(response=response, provider=eave.stdlib.core_api.enums.AuthProvider.google)
    return response


def get_oauth_flow_info() -> oauth_models.OauthFlowInfo:
    """
    https://developers.google.com/identity/protocols/oauth2/web-server#python_1
    """
    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )

    return oauth_models.OauthFlowInfo(authorization_url=authorization_url, state=state)


def decode_id_token(id_token: str) -> GoogleOAuthResponseBody:
    token_json: eave_util.JsonObject = google.oauth2.id_token.verify_oauth2_token(
        id_token=id_token,
        audience=app_config.eave_google_oauth_client_id,
        request=requests.Request(),
    )

    token = GoogleOAuthResponseBody(**token_json)
    return token


def build_flow(state: Optional[str] = None) -> google_auth_oauthlib.flow.Flow:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        app_config.eave_google_oauth_client_credentials,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/openid",
        ],
        redirect_uri=f"{app_config.eave_api_base}/oauth/google/callback",
        state=state,
    )

    return flow
