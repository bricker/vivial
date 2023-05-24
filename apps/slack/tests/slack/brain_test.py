from slack_bolt.async_app import AsyncBoltContext

from eave.slack.brain.core import Brain
from eave.slack.slack_models import SlackMessage
from eave.stdlib.core_api.enums import DocumentPlatform
from eave.stdlib.core_api.models import Team
from .base import BaseTestCase


class BrainTest(BaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_alive(self) -> None:
        eave_team = Team(id=self.anyuuid(), name=self.anystring(), document_platform=DocumentPlatform.confluence)
        slack_context = AsyncBoltContext()
        slack_message = SlackMessage(data={"ts": "123"}, slack_context=slack_context)
        brain = Brain(message=slack_message, eave_team=eave_team)
        assert brain.slack_context == slack_context
        assert brain.message == slack_message
        assert brain.eave_team == eave_team
