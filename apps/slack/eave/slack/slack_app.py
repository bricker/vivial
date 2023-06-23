from typing import Optional

from slack_sdk.web.async_slack_response import AsyncSlackResponse

import eave.slack.event_handlers
import eave.stdlib.core_api.operations.slack as eave_slack
import eave.stdlib.core_api.models.slack
import eave.stdlib.exceptions
from eave.stdlib import cache
from slack_bolt.async_app import AsyncApp, AsyncBoltContext
from slack_bolt.authorization import AuthorizeResult
from slack_sdk.web.async_client import AsyncWebClient

from eave.stdlib.logging import LogContext, eaveLogger

from .config import EAVE_CTX_KEY, app_config


class MissingSlackTeamIdError(Exception):
    pass


class MissingSlackClientError(Exception):
    pass


async def authorize(
    team_id: Optional[str], client: Optional[AsyncWebClient], context: AsyncBoltContext
) -> AuthorizeResult:
    """
    https://slack.dev/bolt-python/concepts#authorization
    https://github.com/slackapi/bolt-python/blob/f8c1b86a81690eb5b12cca40339102d23de1f7de/slack_bolt/middleware/authorization/async_multi_teams_authorization.py#L72-L77
    """
    eave_ctx = LogContext.wrap(context.get(EAVE_CTX_KEY))
    eave_ctx.set(
        {
            "eave_request_id": context.get("eave_request_id"),
            "slack_team_id": context.team_id,
            "slack_user_id": context.user_id,
            "slack_channel_id": context.channel_id,
            "slack_bot_id": context.bot_id,
            "slack_bot_user_id": context.bot_user_id,
            "slack_bot_token": f"{context.bot_token[0:5]}..." if context.bot_token else None,
            "slack_user_token": f"{context.user_token[0:5]}..." if context.user_token else None,
        }
    )
    eaveLogger.debug("slack authorize request", eave_ctx)

    # TODO: team_id can be None for org-wide installed apps
    # https://slack.dev/bolt-python/api-docs/slack_bolt/authorization/async_authorize.html
    if team_id is None:
        raise MissingSlackTeamIdError()

    if client is None:
        raise MissingSlackClientError()

    cachekey = f"slack:{team_id}:installation"
    cached_data: str | None = None
    try:
        cached_data = await cache.client().get(cachekey)
        eaveLogger.debug(f"cache hit: {cachekey}", eave_ctx)
    except Exception as e:
        eaveLogger.exception(e, eave_ctx)
        # fall back to making the API requests

    # Notes:
    # - context.bot_id, context.bot_token, and context.bot_user_id are all None in this function.
    # - context.team_id and context.user_id are available (barring org-wide installs mentioned above)

    installation_data: eave_slack.GetSlackInstallation.ResponseBody | None = None
    auth_response: AsyncSlackResponse | None = None

    # The idea here is that we check the cache, and check if the cached token is valid.
    # But, if the cache is inaccessible, the cachekey is missing, or the token isn't valid, we fall back to the API method.
    if cached_data:
        try:
            # If there is cached data, inflate the object and do an auth test.
            installation_data = eave_slack.GetSlackInstallation.ResponseBody.parse_raw(cached_data)
            auth_response = (await client.auth_test(token=installation_data.slack_integration.bot_token)).validate()
        except Exception as e:
            eaveLogger.warning(e, eave_ctx)
            await cache.client().delete(cachekey)
            cached_data = None
            installation_data = None
            auth_response = None
            # fallback to API request

    if installation_data is None:
        # Raises for non-OK response.
        installation_data = await eave_slack.GetSlackInstallation.perform(
            ctx=eave_ctx,
            origin=app_config.eave_origin,
            input=eave_slack.GetSlackInstallation.RequestBody(
                slack_integration=eave.stdlib.core_api.models.slack.SlackInstallationInput(
                    slack_team_id=team_id,
                ),
            ),
        )

    if auth_response is None:
        auth_response = (await client.auth_test(token=installation_data.slack_integration.bot_token)).validate()

    # After we've validated that the auth is good, cache the new data.
    if cached_data is None:  # if the data is already cached, we don't need to add it back
        try:
            # expires cache entries in 12 hours since that is the valid lifetime of a slack auth token
            ttl_12_hours = 12 * 60 * 60
            await cache.client().set(name=cachekey, value=installation_data.json(), ex=ttl_12_hours)
        except Exception as e:
            eaveLogger.exception(e, eave_ctx)

    context["eave_team"] = installation_data.team

    # The following block of code is copied from
    # https://github.com/slackapi/bolt-python/blob/076efb5b0b6db849b074752cec0d406d3c747627/slack_bolt/authorization/authorize_result.py#L62-L93
    bot_user_id: Optional[str] = auth_response.get("user_id") if auth_response.get("bot_id") is not None else None
    user_id: Optional[str] = auth_response.get("user_id") if auth_response.get("bot_id") is None else None

    return AuthorizeResult(
        enterprise_id=auth_response.get("enterprise_id"),
        team_id=auth_response.get("team_id"),
        bot_id=auth_response.get("bot_id"),
        bot_user_id=bot_user_id,
        user_id=user_id,
        bot_token=installation_data.slack_integration.bot_token,
        user_token=None,
    )


signing_secret = app_config.eave_slack_app_signing_secret

# A few things to note about this configuration:
# Most importantly, this app is _not_ used directly to handle incoming event requests from Slack. It is used only during background processing.
# Because of that, there are a few things that are disabled:
# - Request Verification is disabled because:
#   1. We already do it in the Slack Events endpoint
#   2. The Request Verification middleware is time-sensitive, using the x-slack-request-timestamp header. Requests fail validation after 5 minutes of the original request time.
# - The signing secret isn't passed in because it's used for Request Verification, which is disabled
# - SSL Check only adds an endpoint used by Slack to verify that the endpoint is accessible over HTTPS. It's used by Slack in real-time, so enabling it on a background queue is useless.
# - URL Verification only adds an endpoint used by Slack to verify that the endpoint is owned by the app owner, and is disabled for the same reason as the SSL Check middleware.
# All of the above middlewares are handled manually in the Slack Event API endpoint.
# Additionally, `process_before_response` is ENABLED because we're already running this in the background, and we specifically do not want to return a response until the event is done being processed.
# This allows Cloud Tasks to retry the task in case of a failure.
app = AsyncApp(
    # signing_secret=signing_secret,
    process_before_response=True,
    ssl_check_enabled=False,
    request_verification_enabled=False,
    url_verification_enabled=False,
    ignoring_self_events_enabled=True,
    authorize=authorize,
)

eave.slack.event_handlers.register_event_handlers(app=app)
