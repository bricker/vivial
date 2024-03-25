from eave.stdlib.config import SHARED_CONFIG
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.endpoints import Endpoint, EndpointConfiguration


class GithubAppEndpointConfiguration(EndpointConfiguration):
    def __init__(
        self,
        path: str,
        method: str = "POST",
        auth_required: bool = True,
        team_id_required: bool = True,
        signature_required: bool = True,
        origin_required: bool = True,
    ) -> None:
        super().__init__(
            base_url=SHARED_CONFIG.eave_internal_service_base(EaveApp.eave_github_app),
            path=path,
            audience=EaveApp.eave_github_app,
            method=method,
            auth_required=auth_required,
            team_id_required=team_id_required,
            signature_required=signature_required,
            origin_required=origin_required,
        )


class GithubAppEndpoint(Endpoint):
    config: GithubAppEndpointConfiguration
