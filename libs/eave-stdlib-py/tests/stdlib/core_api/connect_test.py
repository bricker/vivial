

from pydantic import ValidationError
from eave.stdlib.core_api.models.connect import AtlassianProduct, QueryConnectInstallationInput
from eave.stdlib.test_util import UtilityBaseTestCase


class CoreApiConnectTest(UtilityBaseTestCase):
    async def asyncSetUp(self):
        await super().asyncSetUp()

    async def test_query_input_model_validation(self):
        valid_model1 = QueryConnectInstallationInput(
            product=AtlassianProduct.jira,
            team_id=self.anystring("team_id"),
            client_key=None,
        )
        assert valid_model1 # no error raised

        valid_model2 = QueryConnectInstallationInput(
            product=AtlassianProduct.jira,
            team_id=None,
            client_key=self.anystring("client_key"),
        )
        assert valid_model2 # no error raised

        valid_model3 = QueryConnectInstallationInput(
            product=AtlassianProduct.jira,
            team_id=self.anystring("team_id"),
            client_key=self.anystring("client_key"),
        )
        assert valid_model3 # no error raised

        with self.assertRaises(ValidationError):
            invalid_model = QueryConnectInstallationInput(
                product=AtlassianProduct.jira,
                team_id=None,
                client_key=None,
            )
            assert not invalid_model # This will never be reached, this line is here to help understand this test case
