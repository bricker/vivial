import eave.slack.event_handlers
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from slack_bolt.authorization import AuthorizeResult

from .config import app_config

# move this somewhere?
async def authorize(enterprise_id, team_id, logger) -> AuthorizeResult:
    # TODO: make req to /slack_sources/query for bot deets
    res = make req
    if not res:
        logger.error("No authorization information was found")

    # TODO: do we care about enterprise stuff yet??
    # enterprise_id doesn't exist for some teams
    is_valid_enterprise = True if (("enterprise_id" not in team) or (enterprise_id == team["enterprise_id"])) else False
    assert ((is_valid_enterprise == True) and (team["team_id"] == team_id)):
    return AuthorizeResult(
        enterprise_id=enterprise_id,
        team_id=team_id,
        bot_token=team["bot_token"],
        bot_id=team["bot_id"],
        bot_user_id=team["bot_user_id"]
    )
    

token = app_config.eave_slack_bot_token
signing_secret = app_config.eave_slack_app_signing_secret

app = AsyncApp(
    token=token,
    signing_secret=signing_secret,
    url_verification_enabled=True,
    ssl_check_enabled=True,
    ignoring_self_events_enabled=True,
    request_verification_enabled=True,
    authorize=authorize,
)

eave.slack.event_handlers.register_event_handlers(app)

client = app.client

handler = AsyncSlackRequestHandler(app)
