import typing
from dataclasses import dataclass

import eave.stdlib
import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.id_token
import google_auth_oauthlib.flow
import googleapiclient.discovery

from eave.core.internal.config import app_config

from .models import OAuthFlowInfo

_OAUTH_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

_REDIRECT_URI = f"{app_config.eave_api_base}/oauth/google/callback"


class GoogleIdToken:
    """
    https://developers.google.com/identity/openid-connect/openid-connect#authenticatingtheuser
    """

    sub: str
    """Google globally unique and immutable user ID"""
    given_name: typing.Optional[str]
    email: typing.Optional[str]

    def __init__(self, token: eave.stdlib.typing.JsonObject) -> None:
        self.sub = token["sub"]
        self.given_name = token.get("given_name")
        self.email = token.get("email")
        self._token = token


@dataclass
class GoogleOAuthClientConfig:
    """Documentation for the Google Client Config doc format"""

    client_id: str
    project_id: str
    auth_uri: str
    token_uri: str
    auth_provider_x509_cert_url: str
    client_secret: str
    redirect_uris: typing.List[str]


@dataclass
class GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.userinfo.html#get
    """

    email: typing.Optional[str] = None  # The user's email address.
    family_name: typing.Optional[str] = None  # The user's last name.
    gender: typing.Optional[str] = None  # The user's gender.
    given_name: typing.Optional[str] = None  # The user's first name.
    hd: typing.Optional[str] = None  # The hosted domain e.g. example.com if the user is Google apps user.
    id: typing.Optional[str] = None  # The obfuscated ID of the user.
    link: typing.Optional[str] = None  # URL of the profile page.
    locale: typing.Optional[str] = None  # The user's preferred locale.
    name: typing.Optional[str] = None  # The user's full name.
    picture: typing.Optional[str] = None  # URL of the user's picture image.
    verified_email: typing.Optional[
        bool
    ] = None  # Boolean flag which is true if the email address is verified. Always verified because we only return the user's primary email address.


def get_userinfo(credentials: google.oauth2.credentials.Credentials) -> GoogleOAuthV2GetResponse:
    """
    https://googleapis.github.io/google-api-python-client/docs/dyn/oauth2_v2.html
    """
    with googleapiclient.discovery.build("oauth2", "v2", credentials=credentials) as service:
        user_info = service.userinfo().get().execute()

    return GoogleOAuthV2GetResponse(**user_info)


def get_oauth_credentials(access_token: str, refresh_token: str) -> google.oauth2.credentials.Credentials:
    google_oauth_client_config = app_config.eave_google_oauth_client_credentials
    credentials = google.oauth2.credentials.Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=google_oauth_client_config.get("token_uri"),
        client_id=google_oauth_client_config.get("client_id"),
        client_secret=google_oauth_client_config.get("client_secret"),
        scopes=_OAUTH_SCOPES,
    )
    return credentials


def build_flow(state: typing.Optional[str] = None) -> google_auth_oauthlib.flow.Flow:
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        app_config.eave_google_oauth_client_credentials,
        scopes=_OAUTH_SCOPES,
        redirect_uri=_REDIRECT_URI,
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
    token_json: eave.stdlib.typing.JsonObject = google.oauth2.id_token.verify_oauth2_token(
        id_token=id_token,
        audience=app_config.eave_google_oauth_client_id,
        request=google.auth.transport.requests.Request(),
    )

    # TODO: Verify nonce
    token = GoogleIdToken(token=token_json)
    return token
