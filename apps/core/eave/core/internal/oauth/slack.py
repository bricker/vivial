from slack_sdk.oauth import AuthorizeUrlGenerator
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.web.async_slack_response import AsyncSlackResponse
import eave.stdlib.util as eave_util
from eave.core.internal.config import app_config
from typing import Dict, Optional, Self
from eave.stdlib import logger
import slack_sdk.errors

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

    @classmethod
    async def get(cls, token: str, log_context: Optional[Dict[str,str]]) -> Self | None:
        client = AsyncWebClient()
        response = await client.openid_connect_userInfo(
            token=token,
        )

        try:
            response.validate()
        except slack_sdk.errors.SlackApiError as e:
            logger.error("Could not retrieve user identify from Slack", exc_info=e, extra=log_context)
            return None

        return cls(response=response)


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

    def __init__(self, **kwargs: str):
        assert "id" in kwargs
        self.id = kwargs["id"]
        assert "access_token" in kwargs
        self.access_token = kwargs["access_token"]
        self.refresh_token = kwargs.get("refresh_token")

class SlackOAuthResponse:
    bot_token: str
    team: SlackTeam
    authed_user: SlackAuthorizedUser

    def __init__(self, response: AsyncSlackResponse):
        access_token: Optional[str] = response.get("access_token")
        assert access_token is not None
        installed_team: dict[str, str] = response.get("team", {})
        installer: dict[str, str] = response.get("authed_user", {})

        self.bot_token = access_token
        self.team = SlackTeam(**installed_team)
        self.authed_user = SlackAuthorizedUser(**installer)

class SlackAuthTestResponse:
    bot_id: str | None
    bot_user_id: str | None

    def __init__(self, response: AsyncSlackResponse):
        self.bot_id = response.get("bot_id")
        self.bot_user_id = response.get("user_id")
