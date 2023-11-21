from enum import StrEnum
from typing import Optional
from uuid import UUID

import strawberry.federation as sb
from eave.core.graphql.types.mutation_result import MutationResult

from eave.core.internal.orm.api_documentation_jobs import ApiDocumentationJobOrm
import eave.core.internal.database as eave_db


@sb.enum
class LastJobResult(StrEnum):
    none = "none"
    doc_created = "doc_created"
    no_api_found = "no_api_found"
    error = "error"


@sb.enum
class ApiDocumentationJobState(StrEnum):
    running = "running"
    idle = "idle"


@sb.type
class ApiDocumentationJob:
    id: UUID = sb.field()
    team_id: UUID = sb.field()
    github_repo_id: UUID = sb.field()
    state: ApiDocumentationJobState = sb.field()
    last_result: LastJobResult = sb.field()

    @classmethod
    def from_orm(cls, orm: ApiDocumentationJobOrm) -> "ApiDocumentationJob":
        return ApiDocumentationJob(
            id=orm.id,
            team_id=orm.team_id,
            github_repo_id=orm.github_repo_id,
            state=ApiDocumentationJobState(value=orm.state),
            last_result=LastJobResult(value=orm.last_result),
        )

@sb.input
class ApiDocumentationJobListInput:
    id: UUID = sb.field()


@sb.input
class ApiDocumentationJobUpsertInput:
    github_repo_id: UUID = sb.field()
    state: ApiDocumentationJobState = sb.field()
    last_result: Optional[LastJobResult] = sb.field()

@sb.type
class ApiDocumentationJobMutationResult(MutationResult):
    api_documentation_job: ApiDocumentationJob

class ApiDocumentationJobResolvers:
    @staticmethod
    async def get_api_documentation_jobs(team_id: UUID, ids: list[UUID]) -> list[ApiDocumentationJob]:
        ids = [job.id for job in jobs] if (jobs := input.jobs) else None

        async with eave_db.async_session.begin() as db_session:
            docs_job_orms = await ApiDocumentationJobOrm.query(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=team_id,
                    ids=ids,
                ),
            )

        return json_response(
            GetApiDocumentationJobsOperation.ResponseBody(
                jobs=[orm.api_model for orm in list(docs_job_orms)],
            )
        )
    @staticmethod
    async def upsert_api_documentation_job(team_id: UUID, input: ApiDocumentationJobUpsertInput) -> ApiDocumentationJobMutationResult:
        async with eave_db.async_session.begin() as db_session:
            docs_job_orm = await ApiDocumentationJobOrm.one_or_none(
                session=db_session,
                params=ApiDocumentationJobOrm.QueryParams(
                    team_id=team_id,
                    github_repo_id=input.job.github_repo_id,
                ),
            )

            if docs_job_orm is None:
                docs_job_orm = await ApiDocumentationJobOrm.create(
                    session=db_session,
                    team_id=team_id,
                    github_repo_id=input.job.github_repo_id,
                    state=input.job.state,
                )
            else:
                docs_job_orm.update(
                    session=db_session,
                    state=input.job.state,
                    last_result=input.job.last_result,
                )

        return json_response(
            UpsertApiDocumentationJobOperation.ResponseBody(
                job=docs_job_orm.api_model,
            )
        )
