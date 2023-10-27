from eave.stdlib.core_api.models.subscriptions import (
    SubscriptionSource,
    SubscriptionSourceEvent,
    SubscriptionSourcePlatform,
)
from eave.stdlib.core_api.models.subscriptions import (
    Subscription,
)
from eave.stdlib.core_api.models.team import DocumentPlatform, Team
from eave.stdlib.core_api.operations.subscriptions import CreateSubscriptionRequest
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.github_api.operations.content import GetGithubUrlContent
import eave.stdlib.link_handler as link_handler
from eave.stdlib.test_util import UtilityBaseTestCase
import unittest.mock


class TestTaskQueue(UtilityBaseTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()

    async def test_alive(self) -> None:
        pass