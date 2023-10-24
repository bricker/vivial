from eave.stdlib.api_types import ClientApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp


class ConfluenceEndpointConfiguration(ClientApiEndpointConfiguration):
    @property
    def audience(self) -> EaveApp:
        return EaveApp.eave_confluence_app


class ConfluenceApiEndpoint:
    config: ConfluenceEndpointConfiguration
