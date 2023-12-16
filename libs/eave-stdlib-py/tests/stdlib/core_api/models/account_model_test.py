from eave.stdlib.core_api.models.account import AuthProvider
from eave.stdlib.test_util import UtilityBaseTestCase


class CoreApiAccountModelTest(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_auth_provider_values(self):
        """
        These are referenced in cookie names and database strings, so shouldn't change
        """

        assert AuthProvider.google == "google"
        assert AuthProvider.slack == "slack"
        assert AuthProvider.atlassian == "atlassian"
        assert AuthProvider.github == "github"
