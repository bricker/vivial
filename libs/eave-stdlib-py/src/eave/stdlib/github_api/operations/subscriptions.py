from typing import Optional, Unpack
import uuid

from eave.stdlib import requests
from eave.stdlib.api_types import BaseRequestBody, BaseResponseBody
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
        document_reference: Optional[DocumentReference]

    @classmethod
    async def perform(
        cls, input: RequestBody, team_id: uuid.UUID, **kwargs: Unpack[requests.CommonRequestArgs]
    ) -> ResponseBody:
        return await requests.make_request(
            config=cls.config,
            response_type=cls.ResponseBody,
            input=input,
            team_id=team_id,
            **kwargs,
        )
