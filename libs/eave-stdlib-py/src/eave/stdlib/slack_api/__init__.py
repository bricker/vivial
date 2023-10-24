from eave.stdlib.api_types import ServerApiEndpointConfiguration
from eave.stdlib.eave_origins import EaveApp


class SlackAppEndpointConfiguration(ServerApiEndpointConfiguration):
    @property
    def audience(self) -> EaveApp:
        return EaveApp.eave_slack_app


class SlackAppEndpoint:
    config: SlackAppEndpointConfiguration
