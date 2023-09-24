from eave.stdlib.config import shared_config
from eave.stdlib.core_api.operations import Endpoint, EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp

_base_url = shared_config.eave_internal_service_base(EaveApp.eave_github_app)


class GithubAppEndpointConfiguration(EndpointConfiguration):
    audience = EaveApp.eave_github_app

    @property
    def url(self) -> str:
        return f"{_base_url}{self.path}"


class GithubAppEndpoint(Endpoint):
    config: GithubAppEndpointConfiguration
