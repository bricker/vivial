from typing import Unpack

from aiohttp.hdrs import METH_POST

from eave.stdlib.core_api.models.client_credentials import CredentialsAuthMethod
from eave.stdlib.core_api.models.data_collector_config import DataCollectorConfig
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetDataCollectorConfigRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/collector-configs/query",
        method=METH_POST,
        auth_required=False,
        origin_required=False,
        is_public=True,
        creds_auth_method=CredentialsAuthMethod.headers,
    )

    class ResponseBody(BaseResponseBody):
        config: DataCollectorConfig

    @classmethod
    async def perform(
        cls,
        client_id: str,
        client_secret: str,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        addl_headers = kwargs.get("addl_headers") or {}
        addl_headers.update(
            {
                "eave-client-id": client_id,
                "eave-client-secret": client_secret,
            }
        )
        kwargs.update({"addl_headers": addl_headers})

        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
