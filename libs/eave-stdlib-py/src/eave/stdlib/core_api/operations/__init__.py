from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.endpoints import Endpoint, EndpointConfiguration

from ...config import SHARED_CONFIG


class CoreApiEndpointConfiguration(EndpointConfiguration):
    def __init__(
        self,
        *,
        path: str,
        method: str = "POST",
        auth_required: bool = True,
        origin_required: bool = True,
        is_public: bool = False,
    ) -> None:
        super().__init__(
            base_url=SHARED_CONFIG.eave_internal_service_base(EaveApp.eave_api),
            path=path,
            audience=EaveApp.eave_api,
            method=method,
            auth_required=auth_required,
            origin_required=origin_required,
            is_public=is_public,
        )


class CoreApiEndpoint(Endpoint):
    config: CoreApiEndpointConfiguration
