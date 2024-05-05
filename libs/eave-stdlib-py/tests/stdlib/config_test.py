from eave.stdlib.config import SHARED_CONFIG, EaveEnvironment
from eave.stdlib.eave_origins import EaveApp
from .base import StdlibBaseTestCase


class ConfigTest(StdlibBaseTestCase):
    async def test_internal_service_base_non_dev(self):
        project = self.anystr("gcp")
        self.patch_env({"EAVE_ENV": EaveEnvironment.production, "GOOGLE_CLOUD_PROJECT": project})

        assert (
            SHARED_CONFIG.eave_internal_service_base(service=EaveApp.eave_api)
            == f"https://api-dot-{project}.uc.r.appspot.com"
        )
        assert (
            SHARED_CONFIG.eave_internal_service_base(service=EaveApp.eave_dashboard)
            == f"https://dashboard-dot-{project}.uc.r.appspot.com"
        )
        assert (
            SHARED_CONFIG.eave_internal_service_base(service=EaveApp.eave_github_app)
            == f"https://github-dot-{project}.uc.r.appspot.com"
        )
