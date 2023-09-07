from typing import Unpack
import uuid
from ... import requests
from eave.stdlib.core_api.models.github_documents import (
    GithubDocument,
    GithubDocumentsQueryInput,
    GithubDocumentCreateInput,
)
from . import BaseRequestBody, BaseResponseBody, Endpoint, EndpointConfiguration


class GetGithubDocumentsRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-documents/query",
        auth_required=True,
    )

    class RequestBody(BaseRequestBody):
        query_params: GithubDocumentsQueryInput

    class ResponseBody(BaseResponseBody):
        documents: list[GithubDocument]

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateGithubDocumentRequest(Endpoint):
    config = EndpointConfiguration(
        path="/github-documents/create",
        auth_required=True,
    )

    class RequestBody(BaseRequestBody):
        document: GithubDocumentCreateInput

    class ResponseBody(BaseResponseBody):
        document: GithubDocument

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            url=cls.config.url,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)
