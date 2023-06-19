from typing import Optional

from slack_bolt.async_app import AsyncBoltContext
from eave.slack.brain.message_prompts import MessageAction
from eave.slack.config import TASK_EXECUTION_COUNT_CONTEXT_KEY
from eave.slack.slack_models import SlackMessage, SlackProfile
from eave.stdlib import analytics
from eave.stdlib.core_api.models.integrations import Integration
from eave.stdlib.core_api.models.subscriptions import Subscription
import eave.stdlib.core_api.models.team as team
from eave.stdlib.logging import LogContext
from eave.stdlib.typing import JsonObject


class Base:
    """
    Base annotations for all Brain mixins
    """

    message: SlackMessage
    user_profile: Optional[SlackProfile]
    expanded_text: str
    message_context: str
    eave_team: team.Team
    subscriptions: list[Subscription]
    slack_context: AsyncBoltContext
    message_action: Optional[MessageAction] = None
    eave_ctx: LogContext

    def __init__(
        self, message: SlackMessage, eave_team: team.Team, slack_ctx: AsyncBoltContext, eave_ctx: LogContext
    ) -> None:
        self.message = message
        self.eave_team = eave_team
        self.slack_context = slack_ctx
        self.eave_ctx = eave_ctx
        self.subscriptions = []

    def log_event(self, event_name: str, event_description: str, opaque_params: Optional[JsonObject] = None) -> None:
        if opaque_params is None:
            opaque_params = {}

        analytics.log_event(
            event_name=event_name,
            event_description=event_description,
            event_source="slack app",
            eave_team_id=self.eave_team.id,
            opaque_params={
                "integration": Integration.slack.value,
                "request_type": self.message_action.value if self.message_action else None,
                "message_content": self.message.text,
                "message_user_id": self.message.user,
                "message_team": self.message.team,
                "message_channel": self.message.channel,
                **opaque_params,
            },
            ctx=self.eave_ctx,
        )

    @property
    def execution_count(self) -> int:
        count = self.slack_context.get(TASK_EXECUTION_COUNT_CONTEXT_KEY, 0)
        return int(count)
