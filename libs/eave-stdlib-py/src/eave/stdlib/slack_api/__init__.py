from eave.stdlib.config import shared_config
from eave.stdlib.core_api.operations import Endpoint, EndpointConfiguration
from eave.stdlib.eave_origins import EaveApp

_base_url = shared_config.eave_internal_service_base(EaveApp.eave_slack_app)

class SlackAppEndpointConfiguration(EndpointConfiguration):
    audience = EaveApp.eave_slack_app

    @property
    def url(self) -> str:
        return f"{_base_url}{self.path}"

class SlackAppEndpoint(Endpoint):
    config: SlackAppEndpointConfiguration
