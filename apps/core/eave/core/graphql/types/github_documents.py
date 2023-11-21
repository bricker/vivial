import datetime
from enum import StrEnum
from typing import Optional
import uuid

import strawberry.federation as sb
from strawberry.unset import UNSET
from eave.core.graphql.types.mutation_result import MutationResult
from eave.core.internal.orm.github_documents import GithubDocumentsOrm

import eave.core.internal.database as eave_db
from eave.core.internal.orm.github_repos import GithubRepoOrm

@sb.enum
class GithubDocumentStatus(StrEnum):
    PROCESSING = "processing"
    FAILED = "failed"
    PR_OPENED = "pr_opened"
    PR_MERGED = "pr_merged"
    PR_CLOSED = "pr_closed"


@sb.enum
class GithubDocumentType(StrEnum):
    API_DOCUMENT = "api_document"
    ARCHITECTURE_DOCUMENT = "architecture_document"


@sb.type
class GithubDocument:
    id: uuid.UUID = sb.field()
    team_id: uuid.UUID = sb.field()
    github_repo_id: uuid.UUID = sb.field()
    pull_request_number: Optional[int] = sb.field()
    status: GithubDocumentStatus = sb.field()
    status_updated: datetime.datetime = sb.field()
    file_path: Optional[str] = sb.field()
    api_name: Optional[str] = sb.field()
    type: GithubDocumentType = sb.field()

    @classmethod
    def from_orm(cls, orm: GithubDocumentsOrm) -> "GithubDocument":
        return GithubDocument(
            id=orm.id,
            team_id=orm.team_id,
            github_repo_id=orm.github_repo_id,
            pull_request_number=orm.pull_request_number,
            status=GithubDocumentStatus(value=orm.status),
            status_updated=orm.status_updated,
            file_path=orm.file_path,
            api_name=orm.api_name,
            type=GithubDocumentType(value=orm.type),
        )

@sb.type
class GithubDocumentMutationResult(MutationResult):
    github_document: GithubDocument

@sb.input
class GithubDocumentsQueryInput:
    id: Optional[uuid.UUID] = sb.field()
    github_repo_id: Optional[uuid.UUID] = sb.field()
    type: Optional[GithubDocumentType] = sb.field()
    pull_request_number: Optional[int] = sb.field()


@sb.input
class GithubDocumentCreateInput:
    type: GithubDocumentType = sb.field()
    status: Optional[GithubDocumentStatus] = sb.field()
    file_path: Optional[str] = sb.field()
    api_name: Optional[str] = sb.field()
    pull_request_number: Optional[int] = sb.field()


@sb.input
class GithubDocumentValuesInput:
    pull_request_number: Optional[int] = sb.field()
    status: Optional[GithubDocumentStatus] = sb.field()
    file_path: Optional[str] = sb.field()
    api_name: Optional[str] = sb.field()


@sb.input
class GithubDocumentUpdateInput:
    id: uuid.UUID = sb.field()
    new_values: GithubDocumentValuesInput = sb.field()


@sb.input
class GithubDocumentsDeleteByIdsInput:
    id: uuid.UUID = sb.field()


@sb.input
class GithubDocumentsDeleteByTypeInput:
    type: GithubDocumentType = sb.field()

class GithubDocumentResolvers:
    @staticmethod
    async def get_github_documents(team_id: uuid.UUID, query: GithubDocumentsQueryInput) -> list[GithubDocument]:
        async with eave_db.async_session.begin() as db_session:
            github_repo_orm = None
            if input.query_params.github_repo_id:
                github_repo_orm = await GithubRepoOrm.one_or_exception(
                    session=db_session,
                    team_id=team_id,
                    id=query.github_repo_id,
                )

            gh_doc_orms = await GithubDocumentsOrm.query(
                session=db_session,
                params=GithubDocumentsOrm.QueryParams(
                    team_id=team_id,
                    id=query.id,
                    github_repo_id=github_repo_orm.id if github_repo_orm else None,
                    type=query.type,
                    pull_request_number=query.pull_request_number,
                ),
            )

    @staticmethod
    async def create_github_document(team_id: uuid.UUID, github_repo_id: uuid.UUID, github_document: GithubDocumentCreateInput) -> GithubDocumentMutationResult:
        async with eave_db.async_session.begin() as db_session:
            gh_repo_orm = await GithubRepoOrm.one_or_exception(
                session=db_session, team_id=team_id, id=github_repo_id,
            )

            gh_doc_orm = await GithubDocumentsOrm.create(
                session=db_session,
                team_id=team_id,
                github_repo_id=gh_repo_orm.id,
                file_path=input.document.file_path,
                api_name=input.document.api_name,
                type=input.document.type,
                pull_request_number=input.document.pull_request_number,
            )

        return GithubDocumentMutationResult(
            eave_request_id=ctx.eave_request_id,
            github_document=GithubDocument.from_orm(gh_doc_orm),
        )

    @staticmethod
    async def update_github_document(team_id: uuid.UUID, input: GithubDocumentUpdateInput) -> GithubDocumentMutationResult:
        async with eave_db.async_session.begin() as db_session:
            gh_doc_orm = await GithubDocumentsOrm.one_or_exception(
                session=db_session,
                team_id=team_id,
                id=input.id,
            )

            gh_doc_orm.update(input.new_values)

    @staticmethod
    async def delete_github_document(team_id: uuid.UUID, ids: Optional[list[uuid.UUID]] = UNSET, type: Optional[GithubDocumentType] = UNSET) -> MutationResult:
        FIXME
        async with eave_db.async_session.begin() as db_session:
            await GithubDocumentsOrm.delete_by_ids(
                session=db_session,
                team_id=team_id,
                ids=[ensure_uuid(document.id) for document in input.documents],
            )

            await GithubDocumentsOrm.delete_by_type(
                session=db_session,
                team_id=ensure_uuid(unwrap(eave_state.ctx.eave_team_id)),
                type=input.documents.type,
            )
