from eave.stdlib.config import SHARED_CONFIG, EaveEnvironment
from eave.stdlib.eave_origins import EaveApp
from .base import StdlibBaseTestCase


class ConfigTest(StdlibBaseTestCase):
    async def test_public_service_base(self):
        self.patch_env({
            "EAVE_API_BASE_PUBLIC": "https://api.eave.tests",
        }, clear=True)

        assert (
            SHARED_CONFIG.eave_public_service_base(service=EaveApp.eave_api)
            == "https://api.eave.tests"
        )

        # Test the default value
        assert (
            SHARED_CONFIG.eave_public_service_base(service=EaveApp.eave_dashboard)
            == ""
        )

    async def test_internal_service_base(self):
        self.patch_env({
            "EAVE_API_BASE_INTERNAL": "https://api.eave.internal",
        }, clear=True)

        assert (
            SHARED_CONFIG.eave_internal_service_base(service=EaveApp.eave_api)
            == "https://api.eave.internal"
        )

        # Test the default value
        assert (
            SHARED_CONFIG.eave_internal_service_base(service=EaveApp.eave_dashboard)
            == ""
        )
