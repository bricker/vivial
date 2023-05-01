import typing
from typing import Optional

from eave.core.internal.config import app_config
from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse

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

    def __init__(self, response: AsyncSlackResponse) -> None:
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


class SlackTeam:
    id: str
    name: str

    def __init__(self, **kwargs: str):
        assert "id" in kwargs
        self.id = kwargs["id"]
        assert "name" in kwargs
        self.name = kwargs["name"]


class SlackAuthorizedUser:
    id: str
    access_token: str
    refresh_token: Optional[str]
    token_expires_in: Optional[int]

    def __init__(self, **kwargs: typing.Any):
        assert "id" in kwargs
        self.id = kwargs["id"]
        assert "access_token" in kwargs
        self.access_token = kwargs["access_token"]
        self.refresh_token = kwargs.get("refresh_token")
        self.token_expires_in = kwargs.get("expires_in")


class SlackOAuthResponse:
    bot_access_token: str
    bot_refresh_token: Optional[str]
    bot_token_expires_in: Optional[int]
    team: SlackTeam
    authed_user: SlackAuthorizedUser

    def __init__(self, response: AsyncSlackResponse):
        access_token: Optional[str] = response.get("access_token")
        assert access_token is not None
        installed_team: dict[str, str] = response.get("team", {})
        installer: dict[str, str] = response.get("authed_user", {})

        self.bot_access_token = access_token
        self.bot_refresh_token = response.get("refresh_token")
        self.bot_token_expires_in = response.get("expires_in")

        self.team = SlackTeam(**installed_team)
        self.authed_user = SlackAuthorizedUser(**installer)


class SlackAuthTestResponse:
    bot_id: str | None
    bot_user_id: str | None

    def __init__(self, response: AsyncSlackResponse):
        self.bot_id = response.get("bot_id")
        self.bot_user_id = response.get("user_id")


async def get_userinfo_or_exception(token: str) -> SlackIdentity:
    client = AsyncWebClient()
    response = await client.openid_connect_userInfo(
        token=token,
    )

    response.validate()
    return SlackIdentity(response=response)


async def auth_test_or_exception(token: str) -> SlackAuthTestResponse:
    """
    https://api.slack.com/methods/auth.test#errors
    """
    client = AsyncWebClient()
    response = await client.auth_test(token=token)
    response.validate()
    return SlackAuthTestResponse(response=response)


async def get_access_token(
    code: str,
) -> typing.Tuple[SlackOAuthResponse, SlackAuthTestResponse]:
    client = AsyncWebClient()

    # Complete the installation by calling oauth.v2.access API method
    access_token_response = await client.oauth_v2_access(
        client_id=app_config.eave_slack_client_id,
        client_secret=app_config.eave_slack_client_secret,
        code=code,
        redirect_uri=redirect_uri,
    )

    oauth_data = SlackOAuthResponse(response=access_token_response)
    bot_token = oauth_data.bot_access_token

    auth_test_data = await auth_test_or_exception(bot_token)
    return oauth_data, auth_test_data


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

    return SlackOAuthResponse(response=response)
