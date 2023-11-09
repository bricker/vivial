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


# TODO: dont know if need this? just creat the doc job when the repo is created w/ api docs on? or do a upsert on job run?
class CreateApiDocumentationJobEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = CreateApiDocumentationJobRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            github_repo_orm = await GithubRepoOrm.one_or_exception(
                session=db_session,
                team_id=ensure_uuid(eave_state.ctx.eave_team_id),
            )

            docs_job_orm = await ApiDocumentationJobOrm.create(
                session=db_session,
                team_id=ensure_uuid(eave_state.ctx.eave_team_id),
            )


        return json_response(
            CreateApiDocumentationJobRequest.ResponseBody(
                job=docs_job_orm.api_model,
            )
        )


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


# TODO: probs dont need this... just use get for both single and list (will there be any use case for fetch single??)
class ListApiDocumentationJobEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = GetAllTeamsApiDocumentationJobsRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            feature = input.query_params.feature
            state = input.query_params.state

            gh_repo_orms = await ApiDocumentationJobOrm.query(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=None,
                    api_documentation_state=state if feature is ApiDocumentationJobFeature.API_DOCUMENTATION else None,
                    inline_code_documentation_state=state
                    if feature is ApiDocumentationJobFeature.INLINE_CODE_DOCUMENTATION
                    else None,
                    architecture_documentation_state=state
                    if feature is ApiDocumentationJobFeature.ARCHITECTURE_DOCUMENTATION
                    else None,
                ),
            )

        repo_list = list(gh_repo_orms)

        return json_response(
            GetAllTeamsApiDocumentationJobsRequest.ResponseBody(
                repos=[orm.api_model for orm in repo_list],
            )
        )



class UpdateApiDocumentationJobsEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpdateApiDocumentationJobsRequest.RequestBody.parse_obj(body)
        assert eave_state.ctx.eave_team_id, "eave_team_id unexpectedly missing"

        # transform to dict for ease of use
        update_values = {repo.id: repo.new_values for repo in input.repos}

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await ApiDocumentationJobOrm.query(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                    ids=list(map(lambda r: r.id, input.repos)),
                ),
            )

            for gh_repo_orm in gh_repo_orms:
                assert gh_repo_orm.id in update_values, "Received a ApiDocumentationJob ORM that was not requested"
                new_values = update_values[gh_repo_orm.id]

                # fire analytics event for each changed feature
                _event_name = "eave_github_feature_state_change"
                _event_description = "An Eave GitHub App feature was activated/deactivated"
                _event_source = "eave core api"
                
                gh_repo_orm.update(new_values)

        return json_response(
            UpdateApiDocumentationJobsRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )



