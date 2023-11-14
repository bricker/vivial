from typing import Optional, Unpack
import uuid

from eave.stdlib.core_api.models.github_repos import GithubRepo, GithubRepoRefInput
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
        auth_required=False,
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
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class CreateGithubDocumentRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: GithubRepoRefInput
        document: GithubDocumentCreateInput

    class ResponseBody(BaseResponseBody):
        repo: GithubRepo
        document: GithubDocument

    @classmethod
    async def perform(
        cls,
        input: RequestBody,
        team_id: uuid.UUID,
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class UpdateGithubDocumentRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/update",
        auth_required=False,
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
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class DeleteGithubDocumentsByIdsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/delete/id",
        auth_required=False,
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
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            account_id=account_id,
            access_token=access_token,
            team_id=team_id,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body


class DeleteGithubDocumentsByTypeRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/github-documents/delete/type",
        auth_required=False,
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
        account_id: Optional[uuid.UUID],
        access_token: Optional[str],
        **kwargs: Unpack[requests.CommonRequestArgs],
    ) -> ResponseBody:
        response = await requests.make_request(
            config=cls.config,
            input=input,
            team_id=team_id,
            account_id=account_id,
            access_token=access_token,
            **kwargs,
        )

        body = await cls.make_response(response, cls.ResponseBody)
        return body
