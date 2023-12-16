from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.core_api.operations import Endpoint, EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp

_base_url = SHARED_CONFIG.eave_internal_service_base(EaveApp.eave_github_app)


class GithubAppEndpointConfiguration(EndpointConfiguration):
    audience = EaveApp.eave_github_app

    @property
    def url(self) -> str:
        return f"{_base_url}{self.path}"


class GithubAppEndpoint(Endpoint):
    config: GithubAppEndpointConfiguration
