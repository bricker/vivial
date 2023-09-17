from dataclasses import dataclass
from eave.stdlib.config import shared_config
from eave.stdlib.eave_origins import EaveApp

_base_url = shared_config.eave_internal_service_base(EaveApp.eave_github_app)

@dataclass
class GithubAppEndpointConfiguration:
    path: str

    @property
    def url(self) -> str:
        return f"{_base_url}{self.path}"


class GithubAppEndpoint:
    config: GithubAppEndpointConfiguration
