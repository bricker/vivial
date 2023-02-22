import secrets
from dataclasses import dataclass
from typing import Optional, cast

import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
from google.auth.transport import requests

from eave.internal.settings import APP_SETTINGS
from eave.internal.util import JsonObject


@dataclass
class GoogleOauthFlowInfo:
    authorization_url: str
    state: str


def get_oauth_flow_info() -> GoogleOauthFlowInfo:
    """
    https://developers.google.com/identity/protocols/oauth2/web-server#python_1
    """
    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
    )

    return GoogleOauthFlowInfo(authorization_url=authorization_url, state=state)


def get_oauth_credentials(uri: str, state: str) -> google.oauth2.credentials.Credentials:
    flow = build_flow(state=state)
    flow.fetch_token(authorization_response=uri)

    # flow.credentials returns a `google.auth.credentials.Credentials`, which is the base class of
    # google.oauth2.credentials.Credentials and doesn't contain common oauth properties like refresh_token.
    # The `cast` here gives us type hints, autocomplete, etc. for `flow.credentials`
    credentials = cast(google.oauth2.credentials.Credentials, flow.credentials)
    return credentials


def decode_id_token(id_token: str) -> JsonObject:
    token: JsonObject = google.oauth2.id_token.verify_oauth2_token(
        id_token=id_token,
        audience=APP_SETTINGS.eave_google_oauth_client_id,
        request=requests.Request(),
    )

    return token


def build_flow(state: Optional[str] = None) -> google_auth_oauthlib.flow.Flow:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        APP_SETTINGS.eave_google_oauth_client_credentials,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/openid",
        ],
        redirect_uri=f"{APP_SETTINGS.eave_api_base}/_oauth/google/callback",
        state=state,
    )

    return flow
