from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.async_app import AsyncApp

import eave.settings

app = AsyncApp(
    token=eave.settings.APP_SETTINGS.eave_slack_bot_token,
    signing_secret=eave.settings.APP_SETTINGS.eave_slack_bot_signing_secret,
)

client = app.client
handler = AsyncSlackRequestHandler(app)
