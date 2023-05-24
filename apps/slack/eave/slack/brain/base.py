from typing import Optional

from slack_bolt.async_app import AsyncBoltContext
from eave.slack.brain.message_prompts import MessageAction
from eave.slack.slack_models import SlackMessage, SlackProfile
from eave.slack.util import log_context
from eave.stdlib import analytics
import eave.stdlib.core_api.enums
from eave.stdlib.core_api.models import Subscription, Team
from eave.stdlib.typing import JsonObject


class Base:
    """
    Base annotations for all Brain mixins
    """

    message: SlackMessage
    user_profile: Optional[SlackProfile]
    expanded_text: str
    message_context: str
    eave_team: Team
    subscriptions: list[Subscription]
    slack_context: AsyncBoltContext
    message_action: Optional[MessageAction] = None

    def __init__(self, message: SlackMessage, eave_team: Team) -> None:
        self.message = message
        self.eave_team = eave_team
        self.slack_context = message._ctx._context  # FIXME: Make the AsyncBoltContext public
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
                "integration": eave.stdlib.core_api.enums.Integration.slack.value,
                "request_type": self.message_action.value if self.message_action else None,
                "message_content": self.message.text,
                "message_user_id": self.message.user,
                "message_team": self.message.team,
                "message_channel": self.message.channel,
                **opaque_params,
            },
        )

    @property
    def log_extra(self) -> dict[str, Optional[str]]:
        return log_context(self.slack_context)
