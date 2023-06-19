from slack_bolt.async_app import AsyncBoltContext

from eave.slack.brain.core import Brain
from eave.slack.slack_models import SlackMessage
import eave.stdlib.core_api.models.team
from .base import BaseTestCase


class BrainTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_alive(self) -> None:
        eave_team = eave.stdlib.core_api.models.team.Team(
            id=self.anyuuid(),
            name=self.anystring(),
            document_platform=eave.stdlib.core_api.models.team.DocumentPlatform.confluence,
        )
        slack_context = AsyncBoltContext()
        slack_message = SlackMessage(data={"ts": "123"}, slack_ctx=slack_context, eave_ctx=self.eave_ctx)
        brain = Brain(message=slack_message, eave_team=eave_team, slack_ctx=slack_context, eave_ctx=self.eave_ctx)
        assert brain.slack_context == slack_context
        assert brain.message == slack_message
        assert brain.eave_team == eave_team
