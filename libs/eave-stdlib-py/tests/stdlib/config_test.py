from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.test_util import UtilityBaseTestCase
from eave.stdlib.config import EaveEnvironment, shared_config

class ConfigTest(UtilityBaseTestCase):
    async def test_internal_service_base_non_dev(self):
        project = self.anystr("gcp")
        self.patch_env({ "EAVE_ENV": EaveEnvironment.production, "GOOGLE_CLOUD_PROJECT": project })

        assert shared_config.eave_internal_service_base(service=EaveApp.eave_api) == f"https://api-dot-{project}.uc.r.appspot.com"
        assert shared_config.eave_internal_service_base(service=EaveApp.eave_www) == f"https://www-dot-{project}.uc.r.appspot.com"
        assert shared_config.eave_internal_service_base(service=EaveApp.eave_github_app) == f"https://github-dot-{project}.uc.r.appspot.com"
