import typing
from typing import Any, Optional, TypedDict

from eave.core.internal.config import app_config
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient

# Build https://slack.com/oauth/v2/authorize with sufficient query parameters
redirect_uri = f"{app_config.eave_api_base}/oauth/slack/callback"
authorize_url_generator = AuthorizeUrlGenerator(
    client_id=app_config.eave_slack_client_id,
    scopes=[
        "app_mentions:read",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "files:read",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "links.embed:write",
        "links:read",
        "links:write",
        "metadata.message:read",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "reactions:read",
        "reactions:write",
        "team:read",
        "usergroups:read",
        "users.profile:read",
        "users:read",
        "users:read.email",
    ],
    user_scopes=[
        "openid",
        "profile",
        "email",
    ],
    redirect_uri=redirect_uri,
)


class SlackIdentity:
    """
    https://api.slack.com/methods/openid.connect.userInfo
    """

    ok: Optional[bool]
    sub: Optional[str]
    slack_user_id: Optional[str]
    slack_team_id: Optional[str]
    email: Optional[str]
    email_verified: Optional[bool]
    date_email_verified: Optional[int]
    name: Optional[str]
    picture: Optional[str]
    given_name: Optional[str]
    family_name: Optional[str]
    locale: Optional[str]
    slack_team_name: Optional[str]
    slack_team_domain: Optional[str]
    slack_user_image_24: Optional[str]
    slack_user_image_32: Optional[str]
    slack_user_image_48: Optional[str]
    slack_user_image_72: Optional[str]
    slack_user_image_192: Optional[str]
    slack_user_image_512: Optional[str]
    slack_team_image_34: Optional[str]
    slack_team_image_44: Optional[str]
    slack_team_image_68: Optional[str]
    slack_team_image_88: Optional[str]
    slack_team_image_102: Optional[str]
    slack_team_image_132: Optional[str]
    slack_team_image_230: Optional[str]
    slack_team_image_default: Optional[bool]

    def __init__(self, response: dict[str, Any]) -> None:
        self.ok = response.get("ok")
        self.sub = response.get("sub")
        self.slack_user_id = response.get("https://slack.com/user_id")
        self.slack_team_id = response.get("https://slack.com/team_id")
        self.email = response.get("email")
        self.email_verified = response.get("email_verified")
        self.date_email_verified = response.get("date_email_verified")
        self.name = response.get("name")
        self.picture = response.get("picture")
        self.given_name = response.get("given_name")
        self.family_name = response.get("family_name")
        self.locale = response.get("locale")
        self.slack_team_name = response.get("https://slack.com/team_name")
        self.slack_team_domain = response.get("https://slack.com/team_domain")
        self.slack_user_image_24 = response.get("https://slack.com/user_image_24")
        self.slack_user_image_32 = response.get("https://slack.com/user_image_32")
        self.slack_user_image_48 = response.get("https://slack.com/user_image_48")
        self.slack_user_image_72 = response.get("https://slack.com/user_image_72")
        self.slack_user_image_192 = response.get("https://slack.com/user_image_192")
        self.slack_user_image_512 = response.get("https://slack.com/user_image_512")
        self.slack_team_image_34 = response.get("https://slack.com/team_image_34")
        self.slack_team_image_44 = response.get("https://slack.com/team_image_44")
        self.slack_team_image_68 = response.get("https://slack.com/team_image_68")
        self.slack_team_image_88 = response.get("https://slack.com/team_image_88")
        self.slack_team_image_102 = response.get("https://slack.com/team_image_102")
        self.slack_team_image_132 = response.get("https://slack.com/team_image_132")
        self.slack_team_image_230 = response.get("https://slack.com/team_image_230")
        self.slack_team_image_default = response.get("https://slack.com/team_image_default")


class SlackTeam(TypedDict):
    id: str
    name: str


class SlackAuthorizedUser(TypedDict):
    id: str
    access_token: str
    refresh_token: Optional[str]
    expires_in: Optional[int]


class SlackOAuthResponse(TypedDict):
    access_token: str
    refresh_token: Optional[str]
    expires_in: Optional[int]
    team: SlackTeam
    authed_user: SlackAuthorizedUser


def get_authenticated_client(access_token: str) -> AsyncWebClient:
    client = AsyncWebClient(token=access_token)
    return client


async def get_userinfo_or_exception(access_token: str) -> SlackIdentity:
    client = AsyncWebClient()
    response = await client.openid_connect_userInfo(
        token=access_token,
    )

    response.validate()
    assert isinstance(response.data, dict)
    return SlackIdentity(response=response.data)


async def get_access_token(
    code: str,
) -> SlackOAuthResponse:
    client = AsyncWebClient()

    # Complete the installation by calling oauth.v2.access API method
    response = await client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )

    response.validate()
    oauth_data = typing.cast(SlackOAuthResponse, response.data)
    return oauth_data


async def refresh_access_token(
    refresh_token: str,
) -> SlackOAuthResponse:
    client = AsyncWebClient()

    response = await client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        grant_type="refresh_token",
        refresh_token=refresh_token,
    )

    response.validate()
    return typing.cast(SlackOAuthResponse, response.data)
