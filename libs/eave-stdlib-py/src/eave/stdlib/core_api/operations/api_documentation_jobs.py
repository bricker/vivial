from typing import Unpack, Optional
import uuid
from ... import requests
from eave.stdlib.core_api.models.api_documentation_jobs import (
    ApiDocumentationJob,
    ApiDocumentationJobCreateInput,
    ApiDocumentationJobListInput,
    ApiDocumentationJobsDeleteInput,
    ApiDocumentationJobUpdateInput,
    ApiDocumentationJobsFeatureStateInput,
)
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration


class GetApiDocumentationJobsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/api-documentation-job/query",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repos: Optional[list[ApiDocumentationJobListInput]] = None

    class ResponseBody(BaseResponseBody):
        repos: list[ApiDocumentationJob]

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



class CreateApiDocumentationJobRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/api-documentation-job/create",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repo: ApiDocumentationJobCreateInput

    class ResponseBody(BaseResponseBody):
        repo: ApiDocumentationJob

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



class UpdateApiDocumentationJobsRequest(CoreApiEndpoint):
    config = CoreApiEndpointConfiguration(
        path="/api-documentation-job/update",
        auth_required=False,
    )

    class RequestBody(BaseRequestBody):
        repos: list[ApiDocumentationJobUpdateInput]

    class ResponseBody(BaseResponseBody):
        repos: list[ApiDocumentationJob]

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
