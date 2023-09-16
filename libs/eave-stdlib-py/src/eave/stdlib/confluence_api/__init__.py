from eave.stdlib.core_api.operations import EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp
from ..config import shared_config

_base_url = shared_config.eave_internal_service_base(EaveApp.eave_confluence_app)


class ConfluenceEndpointConfiguration(EndpointConfiguration):
    @property
    def url(self) -> str:
        return f"{_base_url}/confluence/api{self.path}"


class ConfluenceEndpoint:
    config: ConfluenceEndpointConfiguration
