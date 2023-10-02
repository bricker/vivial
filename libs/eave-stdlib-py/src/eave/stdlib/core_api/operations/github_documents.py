from typing import Unpack
import uuid
from ... import requests
from eave.stdlib.core_api.models.github_documents import (
    GithubDocument,
    GithubDocumentsDeleteByIdsInput,
    GithubDocumentsDeleteByTypeInput,
    GithubDocumentsQueryInput,
    GithubDocumentCreateInput,
    GithubDocumentUpdateInput,
)
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration


class GetGithubDocumentsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/query",
    )

    class RequestBody(BaseRequestBody):
        query_params: GithubDocumentsQueryInput

    class ResponseBody(BaseResponseBody):
        documents: list[GithubDocument]

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID | str,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class CreateGithubDocumentRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/create",
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
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class UpdateGithubDocumentRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/update",
    )

    class RequestBody(BaseRequestBody):
        document: GithubDocumentUpdateInput

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
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        response_json = await response.json()
        return cls.ResponseBody(**response_json, _raw_response=response)


class DeleteGithubDocumentsByIdsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/delete/id",
    )

    class RequestBody(BaseRequestBody):
        documents: list[GithubDocumentsDeleteByIdsInput]

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)


class DeleteGithubDocumentsByTypeRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/delete/type",
    )

    class RequestBody(BaseRequestBody):
        documents: GithubDocumentsDeleteByTypeInput

    class ResponseBody(BaseResponseBody):
        pass

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            **kwargs,
        )

        return cls.ResponseBody(_raw_response=response)
