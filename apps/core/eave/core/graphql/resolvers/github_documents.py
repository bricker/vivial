from http import HTTPStatus
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from eave.core.internal import database
from eave.core.internal.orm.github_documents import GithubDocumentsOrm
from eave.core.internal.orm.github_repos import GithubRepoOrm

if TYPE_CHECKING:
    from eave.core.graphql.types.team import Team
    from eave.core.graphql.types.github_document import GithubDocument, GithubDocumentType

async def get_github_documents_for_team(*, root: Team,
    id: Optional[UUID] = None,
    github_repo_id: Optional[UUID] = None,
    type: Optional[GithubDocumentType] = None,
    pull_request_number: Optional[int] = None,
) -> list[GithubDocument]:
    async with database.async_session.begin() as db_session:
        github_repo_orm = None
        if input.query_params.github_repo_id:
            github_repo_orm = await GithubRepoOrm.one_or_exception(
                session=db_session,
                team_id=root.id,
                id=github_repo_id,
            )

        gh_doc_orms = await GithubDocumentsOrm.query(
            session=db_session,
            params=GithubDocumentsOrm.QueryParams(
                team_id=ensure_uuid(eave_state.ctx.eave_team_id),
                id=input.query_params.id,
                github_repo_id=github_repo_orm.id if github_repo_orm else None,
                type=input.query_params.type,
                pull_request_number=input.query_params.pull_request_number,
            ),
        )

    return json_response(
        GetGithubDocumentsRequest.ResponseBody(
            documents=[orm.api_model for orm in gh_doc_orms],
        )
    )


async def create_github_document(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = CreateGithubDocumentRequest.RequestBody.parse_obj(body)

    async with database.async_session.begin() as db_session:
        gh_repo_orm = await GithubRepoOrm.one_or_exception(
            session=db_session, team_id=ensure_uuid(eave_state.ctx.eave_team_id), id=input.repo.id
        )

        gh_doc_orm = await GithubDocumentsOrm.create(
            session=db_session,
            team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
            github_repo_id=gh_repo_orm.id,
            file_path=input.document.file_path,
            api_name=input.document.api_name,
            type=input.document.type,
            pull_request_number=input.document.pull_request_number,
        )

    return json_response(
        CreateGithubDocumentRequest.ResponseBody(
            repo=gh_repo_orm.api_model,
            document=gh_doc_orm.api_model,
        )
    )


async def update_github_document(request: Request) -> Response:
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


async def delete_github_documents_by_ids(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = DeleteGithubDocumentsByIdsRequest.RequestBody.parse_obj(body)

    async with database.async_session.begin() as db_session:
        await GithubDocumentsOrm.delete_by_ids(
            session=db_session,
            team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
            ids=[ensure_uuid(document.id) for document in input.documents],
        )

    return Response(status_code=HTTPStatus.OK)


async def delete_github_documents_by_type(request: Request) -> Response:
    eave_state = EaveRequestState.load(request=request)
    body = await request.json()
    input = DeleteGithubDocumentsByTypeRequest.RequestBody.parse_obj(body)

    async with database.async_session.begin() as db_session:
        await GithubDocumentsOrm.delete_by_type(
            session=db_session,
            team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
            type=input.documents.type,
        )

    return Response(status_code=HTTPStatus.OK)
