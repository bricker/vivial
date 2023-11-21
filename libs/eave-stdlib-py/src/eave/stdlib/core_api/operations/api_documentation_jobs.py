from typing import Unpack, Optional
import uuid
from ... import requests
from eave.stdlib.core_api.models.api_documentation_jobs import (
    ApiDocumentationJob,
    ApiDocumentationJobUpsertInput,
    ApiDocumentationJobListInput,
)
from . import BaseRequestBody, BaseResponseBody, CoreApiEndpoint, CoreApiEndpointConfiguration


# class GetApiDocumentationJobsOperation(CoreApiEndpoint):
#     config = CoreApiEndpointConfiguration(
#         path="/api-documentation-job/query",
#         auth_required=False,
#     )

#     class RequestBody(BaseRequestBody):
#         jobs: Optional[list[ApiDocumentationJobListInput]] = None

#     class ResponseBody(BaseResponseBody):
#         jobs: list[ApiDocumentationJob]

#     @classmethod
#     async def perform(
#         cls,
#         input: RequestBody,
#         team_id: uuid.UUID | str,
#         account_id: Optional[uuid.UUID],
#         access_token: Optional[str],
#         **kwargs: Unpack[requests.CommonRequestArgs],
#     ) -> ResponseBody:
#         response = await requests.make_request(
#             config=cls.config,
#             input=input,
#             team_id=team_id,
#             account_id=account_id,
#             access_token=access_token,
#             **kwargs,
#         )

#         body = await cls.make_response(response, cls.ResponseBody)
#         return body


# class UpsertApiDocumentationJobOperation(CoreApiEndpoint):
#     config = CoreApiEndpointConfiguration(
#         path="/api-documentation-job/upsert",
#         auth_required=False,
#     )

#     class RequestBody(BaseRequestBody):
#         job: ApiDocumentationJobUpsertInput

#     class ResponseBody(BaseResponseBody):
#         job: ApiDocumentationJob

#     @classmethod
#     async def perform(
#         cls,
#         input: RequestBody,
#         team_id: uuid.UUID | str,
#         account_id: Optional[uuid.UUID],
#         access_token: Optional[str],
#         **kwargs: Unpack[requests.CommonRequestArgs],
#     ) -> ResponseBody:
#         response = await requests.make_request(
#             config=cls.config,
#             input=input,
#             team_id=team_id,
#             account_id=account_id,
#             access_token=access_token,
#             **kwargs,
#         )

#         body = await cls.make_response(response, cls.ResponseBody)
#         return body
