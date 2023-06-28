from eave.stdlib.core_api.operations import EndpointConfiguration
from eave.stdlib.eave_origins import EaveService
from eave.stdlib.requests import appengine_base_url


_base_url = appengine_base_url(EaveService.confluence)

class ConfluenceEndpointConfiguration(EndpointConfiguration):
    @property
    def url(self) -> str:
        return f"{_base_url}/confluence/api{self.path}"


class ConfluenceEndpoint:
    config: ConfluenceEndpointConfiguration
