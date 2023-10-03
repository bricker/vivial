from http import HTTPStatus
from eave.core.internal import database
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.stdlib.core_api.models.github_repos import Feature, State
from eave.stdlib.eave_origins import EaveApp
from eave.stdlib.github_api.models import GithubRepoInput
from eave.stdlib.github_api.operations.tasks import RunApiDocumentationTask
from eave.stdlib.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.analytics import log_event
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.github_repos import (
    CreateGithubRepoRequest,
    GetAllTeamsGithubReposRequest,
    GetGithubReposRequest,
    UpdateGithubReposRequest,
    DeleteGithubReposRequest,
    FeatureStateGithubReposRequest,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import unwrap, ensure_uuid


class CreateGithubRepoEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = CreateGithubRepoRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_repo_orm = await GithubRepoOrm.create(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_id=input.repo.external_repo_id,
                github_install_id=input.repo.github_install_id,
                display_name=input.repo.display_name,
                api_documentation_state=input.repo.api_documentation_state,
                inline_code_documentation_state=input.repo.inline_code_documentation_state,
                architecture_documentation_state=input.repo.architecture_documentation_state,
            )

        return json_response(
            CreateGithubRepoRequest.ResponseBody(
                repo=gh_repo_orm.api_model,
            )
        )


class GetGithubRepoEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = GetGithubReposRequest.RequestBody.parse_obj(body)

        external_repo_ids = [repo.external_repo_id for repo in repos] if (repos := input.repos) else None

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_ids=external_repo_ids,
            )

        return json_response(
            GetGithubReposRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )


class GetAllTeamsGithubRepoEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        body = await request.json()
        input = GetAllTeamsGithubReposRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            feature = input.query_params.feature
            state = input.query_params.state

            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                api_documentation_state=state if feature is Feature.API_DOCUMENTATION else None,
                inline_code_documentation_state=state if feature is Feature.INLINE_CODE_DOCUMENTATION else None,
                architecture_documentation_state=state if feature is Feature.ARCHITECTURE_DOCUMENTATION else None,
            )

        return json_response(
            GetAllTeamsGithubReposRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )


class FeatureStateGithubReposEndpoint(HTTPEndpoint):
    """Query if for a given `team_id` all their repos have the specified `state` for the provided `feature`."""

    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = FeatureStateGithubReposRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            state = await GithubRepoOrm.all_repos_match_feature_state(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                feature=input.query_params.feature,
                state=input.query_params.state,
            )

        return json_response(
            FeatureStateGithubReposRequest.ResponseBody(
                states_match=state,
            )
        )


class UpdateGithubReposEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpdateGithubReposRequest.RequestBody.parse_obj(body)

        # transform to dict for ease of use
        update_values = {repo.external_repo_id: repo.new_values for repo in input.repos}

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.query(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_ids=list(update_values.keys()),
            )

            for gh_repo_orm in gh_repo_orms:
                assert gh_repo_orm.external_repo_id in update_values, "Received a GithubRepo ORM that was not requested"
                new_values = update_values[gh_repo_orm.external_repo_id]

                # fire analytics event for each changed feature
                _event_name = "eave_github_feature_state_change"
                _event_description = "An Eave GitHub App feature was activated/deactivated"
                _event_source = "eave core api"
                if new_values.api_documentation_state is not None:
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": Feature.API_DOCUMENTATION.value,
                            "new_state": new_values.api_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )
                if new_values.architecture_documentation_state is not None:
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": Feature.ARCHITECTURE_DOCUMENTATION.value,
                            "new_state": new_values.architecture_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )
                if new_values.inline_code_documentation_state is not None:
                    await log_event(
                        event_name=_event_name,
                        event_description=_event_description,
                        event_source=_event_source,
                        opaque_params={
                            "feature": Feature.INLINE_CODE_DOCUMENTATION.value,
                            "new_state": new_values.inline_code_documentation_state.value,
                            "external_repo_id": gh_repo_orm.external_repo_id,
                        },
                        ctx=eave_state.ctx,
                    )

                if gh_repo_orm.api_documentation_state == State.DISABLED and new_values.api_documentation_state == State.ENABLED:
                    await RunApiDocumentationTask.perform(
                        team_id=gh_repo_orm.team_id,
                        ctx=eave_state.ctx,
                        origin=EaveApp.eave_api,
                        input=RunApiDocumentationTask.RequestBody(
                            repo=GithubRepoInput(external_repo_id=gh_repo_orm.external_repo_id)
                        ),
                    )
                gh_repo_orm.update(new_values)

        return json_response(
            UpdateGithubReposRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )


class DeleteGithubReposEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = DeleteGithubReposRequest.RequestBody.parse_obj(body)

        external_repo_ids = [repo.external_repo_id for repo in input.repos]

        async with database.async_session.begin() as db_session:
            await GithubRepoOrm.delete_by_repo_ids(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_ids=external_repo_ids,
            )

        return Response(status_code=HTTPStatus.OK)
