from dataclasses import dataclass

import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import googleapiclient.discovery

from eave.core.internal.config import CORE_API_APP_CONFIG
from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.typing import JsonObject
from eave.stdlib.util import erasetype

from .models import OAuthFlowInfo

_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

GOOGLE_OAUTH_AUTHORIZE_PATH = "/oauth/google/authorize"
GOOGLE_OAUTH_CALLBACK_PATH = "/oauth/google/callback"
GOOGLE_OAUTH_CALLBACK_URI = f"{SHARED_CONFIG.eave_api_base_url_public}{GOOGLE_OAUTH_CALLBACK_PATH}"


# https://developers.google.com/identity/protocols/oauth2


class GoogleIdToken:
    """
    https://developers.google.com/identity/openid-connect/openid-connect#authenticatingtheuser
    """

    sub: str
    """Google globally unique and immutable user ID"""
    given_name: str | None
    family_name: str | None
    email: str | None

    def __init__(self, data: JsonObject) -> None:
        self.sub = erasetype(data, "sub", "")
        self.given_name = erasetype(data, "given_name")
        self.email = erasetype(data, "email")
        self.family_name = erasetype(data, "family_name")


@dataclass
class GoogleOAuthClientConfig:
    """Documentation for the Google Client Config doc format"""

    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: list[str]


@dataclass
class GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.userinfo.html#get
    """

    email: str | None = None  # The user's email address.
    family_name: str | None = None  # The user's last name.
    gender: str | None = None  # The user's gender.
    given_name: str | None = None  # The user's first name.
    hd: str | None = None  # The hosted domain e.g. example.com if the user is Google apps user.
    id: str | None = None  # The obfuscated ID of the user.
    link: str | None = None  # URL of the profile page.
    locale: str | None = None  # The user's preferred locale.
    name: str | None = None  # The user's full name.
    picture: str | None = None  # URL of the user's picture image.
    verified_email: bool | None = None  # Boolean flag which is true if the email address is verified. Always verified because we only return the user's primary email address.


def get_userinfo(credentials: google.oauth2.credentials.Credentials) -> GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.html
    """
    with googleapiclient.discovery.build("oauth2", "v2", credentials=credentials) as service:
        user_info = service.userinfo().get().execute()

    return GoogleOAuthV2GetResponse(**user_info)


def get_oauth_credentials(access_token: str, refresh_token: str) -> google.oauth2.credentials.Credentials:
    google_oauth_client_config = CORE_API_APP_CONFIG.eave_google_oauth_client_credentials
    creds = google_oauth_client_config["web"]
    token_uri = creds["token_uri"]
    client_id = creds["client_id"]
    client_secret = creds["client_secret"]

    credentials = google.oauth2.credentials.Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=_OAUTH_SCOPES,
    )
    return credentials


def build_flow(state: str | None = None) -> google_auth_oauthlib.flow.Flow:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CORE_API_APP_CONFIG.eave_google_oauth_client_credentials,
        scopes=_OAUTH_SCOPES,
        redirect_uri=GOOGLE_OAUTH_CALLBACK_URI,
        state=state,
    )

    return flow


def get_oauth_flow_info() -> OAuthFlowInfo:
    """
    https://developers.google.com/identity/protocols/oauth2/web-server#python_1
    """
    flow = build_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent",  # forces the consent screen to make sure we get a refresh token
        include_granted_scopes="true",
    )

    return OAuthFlowInfo(authorization_url=authorization_url, state=state)


def decode_id_token(id_token: str) -> GoogleIdToken:
    token_json = google.oauth2.id_token.verify_oauth2_token(
        id_token=id_token,
        audience=CORE_API_APP_CONFIG.eave_google_oauth_client_id,
        request=google.auth.transport.requests.Request(),
    )

    # TODO: Verify nonce
    token = GoogleIdToken(data=token_json)
    return token
