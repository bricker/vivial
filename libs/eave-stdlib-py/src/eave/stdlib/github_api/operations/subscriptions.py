from typing import Optional, Unpack
import uuid

from eave.stdlib import requests
from eave.stdlib.core_api.operations import BaseRequestBody, BaseResponseBody
from . import GithubAppEndpoint, GithubAppEndpointConfiguration
from eave.stdlib.core_api.models.team import Team
from eave.stdlib.core_api.models.subscriptions import Subscription, DocumentReference

class CreateGithubResourceSubscription(GithubAppEndpoint):
    config = GithubAppEndpointConfiguration(
        path="/github/api/subscribe",
    )
    class RequestBody(BaseRequestBody):
        url: str

    class ResponseBody(BaseResponseBody):
        team: Team
        subscription: Subscription
        document_reference: Optional[DocumentReference] = None

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
