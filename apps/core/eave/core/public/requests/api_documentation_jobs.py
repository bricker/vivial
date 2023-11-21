from eave.core.internal import database
from eave.core.internal.orm.api_documentation_jobs import ApiDocumentationJobOrm
from eave.stdlib.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.api_documentation_jobs import (
    UpsertApiDocumentationJobOperation,
    GetApiDocumentationJobsOperation,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid


# class GetApiDocumentationJobEndpoint(HTTPEndpoint):
#     async def post(self, request: Request) -> Response:
#         eave_state = EaveRequestState.load(request=request)
#         body = await request.json()
#         input = GetApiDocumentationJobsOperation.RequestBody.parse_obj(body)

#         ids = [job.id for job in jobs] if (jobs := input.jobs) else None

#         async with database.async_session.begin() as db_session:
#             docs_job_orms = await ApiDocumentationJobOrm.query(
#                 session=db_session,
#                 params=ApiDocumentationJobOrm.QueryParams(
#                     team_id=ensure_uuid(eave_state.ctx.eave_team_id),
#                     ids=ids,
#                 ),
#             )

#         return json_response(
#             GetApiDocumentationJobsOperation.ResponseBody(
#                 jobs=[orm.api_model for orm in list(docs_job_orms)],
#             )
#         )


# class UpsertApiDocumentationJobsEndpoint(HTTPEndpoint):
#     async def post(self, request: Request) -> Response:
#         eave_state = EaveRequestState.load(request=request)
#         body = await request.json()
#         input = UpsertApiDocumentationJobOperation.RequestBody.parse_obj(body)
#         assert eave_state.ctx.eave_team_id, "eave_team_id unexpectedly missing"
#         team_id = ensure_uuid(eave_state.ctx.eave_team_id)

#         async with database.async_session.begin() as db_session:
#             docs_job_orm = await ApiDocumentationJobOrm.one_or_none(
#                 session=db_session,
#                 params=ApiDocumentationJobOrm.QueryParams(
#                     team_id=team_id,
#                     github_repo_id=input.job.github_repo_id,
#                 ),
#             )

#             if docs_job_orm is None:
#                 docs_job_orm = await ApiDocumentationJobOrm.create(
#                     session=db_session,
#                     team_id=team_id,
#                     github_repo_id=input.job.github_repo_id,
#                     state=input.job.state,
#                 )
#             else:
#                 docs_job_orm.update(
#                     session=db_session,
#                     state=input.job.state,
#                     last_result=input.job.last_result,
#                 )

#         return json_response(
#             UpsertApiDocumentationJobOperation.ResponseBody(
#                 job=docs_job_orm.api_model,
#             )
#         )
