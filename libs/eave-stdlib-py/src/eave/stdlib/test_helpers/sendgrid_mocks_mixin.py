from typing import override
import unittest.mock
from eave.stdlib.test_helpers.mocking_mixin import MockingMixin


class SendgridMocksMixin(MockingMixin):
    @override
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self._add_sendgrid_client_mocks()

    def _add_sendgrid_client_mocks(self) -> None:
        self.patch(
            name="SendGridAPIClient.send",
            patch=unittest.mock.patch(
                "sendgrid.SendGridAPIClient.send",
            ),
        )
