from eave.stdlib.api_types import ClientApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp


class GithubAppEndpointConfiguration(ClientApiEndpointConfiguration):
    @property
    def audience(self) -> EaveApp:
        return EaveApp.eave_github_app


class GithubAppEndpoint:
    config: GithubAppEndpointConfiguration
