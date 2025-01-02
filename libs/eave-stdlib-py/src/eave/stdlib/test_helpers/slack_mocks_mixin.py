import unittest.mock
from typing import override

from eave.stdlib.test_helpers.mocking_mixin import MockingMixin


class SlackMocksMixin(MockingMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_slack_client_mocks()

    def _add_slack_client_mocks(self) -> None:
        self.patch(
            name="slack client",
            patch=unittest.mock.patch("slack_sdk.web.async_client.AsyncWebClient.chat_postMessage"),
            return_value={},
        )
