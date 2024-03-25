import uuid
from typing import Optional, Unpack

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
        auth_required=True,
        signature_required=True,
        origin_required=True,
        team_id_required=True,
    )

    class RequestBody(BaseRequestBody):
        return_to: Optional[str]

    @classmethod
    async def perform(
        cls,
        team_id: uuid.UUID | str,
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        input: Optional[RequestBody] = None,
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
        resp.raw_response = response
        return resp
