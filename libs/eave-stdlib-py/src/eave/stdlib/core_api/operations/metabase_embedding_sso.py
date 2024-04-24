import uuid
from typing import Unpack

from eave.stdlib.core_api.operations import (
    CoreApiEndpoint,
    CoreApiEndpointConfiguration,
)
from eave.stdlib.endpoints import BaseRequestBody, BaseResponseBody

from ... import requests_util


class MetabaseEmbeddingSSOOperation(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/oauth/metabase",
        method="GET",
        signature_required=False,
    )

    class RequestBody(BaseRequestBody):
        return_to: str | None

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID | str,
        account_id: uuid.UUID | None,
        access_token: str | None,
        input: RequestBody | None = None,
        **kwargs: Unpack[requests_util.CommonRequestArgs],
    ) -> BaseResponseBody:
        response = await requests_util.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            allow_redirects=False,
            **kwargs,
        )

        resp = BaseResponseBody()
        resp.set_raw_response(response)
        return resp
