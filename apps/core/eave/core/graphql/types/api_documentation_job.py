from uuid import UUID
import strawberry.federation as sb

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
