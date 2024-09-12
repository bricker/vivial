from enum import StrEnum

from eave.stdlib.core_api.models.client_credentials import CredentialsAuthMethod
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.endpoints import Endpoint, EndpointConfiguration

from ...config import SHARED_CONFIG


class CoreApiEndpointConfiguration(EndpointConfiguration):
    def __init__(
        self,
        *,
        path: str,
        method: str,
        auth_required: bool = True,
        origin_required: bool = True,
        creds_auth_method: CredentialsAuthMethod | None = None,
        is_public: bool = False,
    ) -> None:
        super().__init__(
            base_url=SHARED_CONFIG.eave_api_base_url_internal,
            path=path,
            method=method,
            audience=EaveApp.eave_api,
            auth_required=auth_required,
            origin_required=origin_required,
            creds_auth_method=creds_auth_method,
            is_public=is_public,
        )


class CoreApiEndpoint(Endpoint):
    config: CoreApiEndpointConfiguration
