import eave.stdlib
from slack_bolt.async_app import AsyncBoltContext

def log_context(context: AsyncBoltContext) -> eave.stdlib.typing.JsonObject:
    return {
        "json_fields": {
            "slack_team_id": context.team_id,
            "slack_user_id": context.user_id,
            "slack_channel_id": context.channel_id,
            "slack_bot_id": context.bot_id,
            "slack_bot_user_id": context.bot_user_id,
            "slack_bot_token": f"{context.bot_token[0:5]}..." if context.bot_token else None,
            "slack_user_token": f"{context.user_token[0:5]}..." if context.user_token else None,
        }
    }