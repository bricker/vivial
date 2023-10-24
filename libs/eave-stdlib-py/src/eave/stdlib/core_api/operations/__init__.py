from eave.stdlib.api_types import ClientRequestParameters, ServerApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp


class CoreApiEndpointConfiguration(ServerApiEndpointConfiguration):
    @property
    def audience(self) -> EaveApp:
        return EaveApp.eave_api


class CoreApiEndpoint:
    config: CoreApiEndpointConfiguration
