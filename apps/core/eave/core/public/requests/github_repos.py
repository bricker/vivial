from http import HTTPStatus
from eave.core.internal import database
from eave.core.internal.orm.github_repos import GithubRepoOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.github_repos import (
    CreateGithubRepoRequest,
    GetGithubRepoRequest,
    ListGithubReposRequest,
    UpdateGithubRepoRequest,
    DeleteGithubReposRequest,
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
        input = GetGithubRepoRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_repo_orm = await GithubRepoOrm.one_or_exception(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_id=input.repo.external_repo_id,
            )

        return json_response(
            GetGithubRepoRequest.ResponseBody(
                repo=gh_repo_orm.api_model,
            )
        )


class ListGithubReposEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.list_all(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
            )

        return json_response(
            ListGithubReposRequest.ResponseBody(
                repos=[orm.api_model for orm in gh_repo_orms],
            )
        )


class UpdateGithubRepoEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpdateGithubRepoRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_repo_orm = await GithubRepoOrm.one_or_exception(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_id=input.repo.external_repo_id,
            )

            gh_repo_orm.update(input.repo.new_values)

        return json_response(
            UpdateGithubRepoRequest.ResponseBody(
                repo=gh_repo_orm.api_model,
            )
        )


class DeleteGithubReposEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = DeleteGithubReposRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_repo_orms = await GithubRepoOrm.delete_by_repo_ids(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_ids=input.repos.external_repo_ids,
            )

        return Response(status_code=HTTPStatus.OK)
