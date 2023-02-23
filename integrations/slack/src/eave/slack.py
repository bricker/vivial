from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

import eave.event_handlers
import eave.settings

app = AsyncApp(
    token=eave.settings.APP_SETTINGS.eave_slack_bot_token,
    signing_secret=eave.settings.APP_SETTINGS.eave_slack_bot_signing_secret,
)

client = app.client
handler = AsyncSlackRequestHandler(app)

app.event("message")(eave.event_handlers.MessageEventHandler.handler)
app.shortcut("eave_watch_request")(eave.event_handlers.WatchRequestEventHandler.handler)

app.event("app_mention")(eave.event_handlers.NoopEventHandler.handler)
app.event("reaction_added")(eave.event_handlers.NoopEventHandler.handler)
app.event("file_deleted")(eave.event_handlers.NoopEventHandler.handler)
app.event("member_joined_channel")(eave.event_handlers.NoopEventHandler.handler)
