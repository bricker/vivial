from eave.stdlib.core_api.operations import Endpoint, EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp
from ..config import SHARED_CONFIG

_base_url = SHARED_CONFIG.eave_internal_service_base(EaveApp.eave_confluence_app)


class ConfluenceEndpointConfiguration(EndpointConfiguration):
    audience = EaveApp.eave_confluence_app

    @property
    def url(self) -> str:
        return f"{_base_url}/confluence/api{self.path}"


class ConfluenceEndpoint(Endpoint):
    config: ConfluenceEndpointConfiguration
