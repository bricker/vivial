import uuid
from typing import Unpack

from aiohttp.hdrs import METH_POST

from eave.stdlib.core_api.models.data_collector_config import DataCollectorConfig
from eave.stdlib.endpoints import BaseResponseBody

from ... import requests_util
from . import CoreApiEndpoint, CoreApiEndpointConfiguration


class GetMyDataCollectorConfigRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/public/me/collector-configs/query",
        method=METH_POST,
        auth_required=False,
        origin_required=False,  # TODO: add a client sec option?
        is_public=True,
    )

    class ResponseBody(BaseResponseBody):
        config: DataCollectorConfig

    @classmethod
    async def perform(
        cls,
        *,
        account_id: uuid.UUID | str,
        access_token: str,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=None,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
