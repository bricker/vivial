from eave.core.internal import database
from eave.core.internal.orm.github_installation import GithubInstallationOrm
from eave.core.internal.orm.api_documentation_jobs import ApiDocumentationJobOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.github_api.models import ApiDocumentationJobInput
from eave.stdlib.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.analytics import log_event
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.api_documentation_jobs import (
    CreateApiDocumentationJobRequest,
    GetAllTeamsApiDocumentationJobsRequest,
    GetApiDocumentationJobsRequest,
    UpdateApiDocumentationJobsRequest,
    DeleteApiDocumentationJobsRequest,
    FeatureStateApiDocumentationJobsRequest,
)
from eave.stdlib.logging import LogContext
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import ensure_uuid
from eave.core.internal.config import app_config

class GetApiDocumentationJobEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = GetApiDocumentationJobsRequest.RequestBody.parse_obj(body)

        external_repo_ids = [repo.external_repo_id for repo in repos] if (repos := input.repos) else None

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await ApiDocumentationJobOrm.query(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                    external_repo_ids=external_repo_ids,
                ),
            )

        repo_list = list(gh_repo_orms)

        return json_response(
            GetApiDocumentationJobsRequest.ResponseBody(
                repos=[orm.api_model for orm in repo_list],
            )
        )


class UpsertApiDocumentationJobsEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpdateApiDocumentationJobsRequest.RequestBody.parse_obj(body)
        assert eave_state.ctx.eave_team_id, "eave_team_id unexpectedly missing"

        # transform to dict for ease of use
        update_values = {repo.id: repo.new_values for repo in input.repos}

        async with database.async_session.begin() as db_session:
            docs_job_orms = await ApiDocumentationJobOrm.query(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                    ids=list(map(lambda r: r.id, input.repos)),
                ),
            )

            for docs_job_orm in docs_job_orms:
                assert docs_job_orm.id in update_values, "Received a ApiDocumentationJob ORM that was not requested"
                new_values = update_values[docs_job_orm.id]

                
                docs_job_orm.update(new_values)

        return json_response(
            UpdateApiDocumentationJobsRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )



