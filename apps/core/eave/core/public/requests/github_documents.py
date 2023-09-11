from http import HTTPStatus
from eave.core.internal import database
from eave.core.internal.orm.github_documents import GithubDocumentsOrm
from eave.core.public.http_endpoint import HTTPEndpoint
from starlette.requests import Request
from starlette.responses import Response
from eave.stdlib.api_util import json_response
from eave.stdlib.core_api.operations.github_documents import (
    GetGithubDocumentsRequest,
    CreateGithubDocumentRequest,
    UpdateGithubDocumentRequest,
    DeleteGithubDocumentsRequest,
)
from eave.stdlib.request_state import EaveRequestState
from eave.stdlib.util import unwrap, ensure_uuid


class GetGithubDocumentsEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = GetGithubDocumentsRequest.RequestBody.parse_obj(body)

        # query can't take None values, so we only pass parameters
        # that aren't None by destructuring a dict as kwargs
        kwargs = {k: v for k, v in vars(input.query_params).items() if v is not None}

        async with database.async_session.begin() as db_session:
            gh_doc_orms = await GithubDocumentsOrm.query(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                **kwargs,
            )

        return json_response(
            GetGithubDocumentsRequest.ResponseBody(
                documents=[orm.api_model for orm in gh_doc_orms],
            )
        )


class CreateGithubDocumentEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = CreateGithubDocumentRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_doc_orm = await GithubDocumentsOrm.create(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                external_repo_id=input.document.external_repo_id,
                file_path=input.document.file_path,
                api_name=input.document.api_name,
                type=input.document.type,
                pull_request_number=input.document.pull_request_number,
            )

        return json_response(
            CreateGithubDocumentRequest.ResponseBody(
                document=gh_doc_orm.api_model,
            )
        )


class UpdateGithubDocumentEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = UpdateGithubDocumentRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            gh_doc_orm = await GithubDocumentsOrm.one_or_exception(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                id=ensure_uuid(input.document.id),
            )

            gh_doc_orm.update(input.document.new_values)

        return json_response(
            UpdateGithubDocumentRequest.ResponseBody(
                document=gh_doc_orm.api_model,
            )
        )


class DeleteGithubDocumentsEndpoint(HTTPEndpoint):
    async def post(self, request: Request) -> Response:
        eave_state = EaveRequestState.load(request=request)
        body = await request.json()
        input = DeleteGithubDocumentsRequest.RequestBody.parse_obj(body)

        async with database.async_session.begin() as db_session:
            await GithubDocumentsOrm.delete_by_ids(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                ids=[ensure_uuid(document.id) for document in input.documents],
            )

        return Response(status_code=HTTPStatus.OK)
