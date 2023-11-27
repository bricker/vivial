from uuid import UUID
import strawberry.federation as sb

@sb.input
class TeamInput:
    name: Optional[str] = sb.field()
    document_platform: Optional[str] = sb.field()

@sb.type(keys=["id"], name="Team")
class TeamGraphQLType:
    id: UUID = sb.field()
    name: str = sb.field()
    document_platform: Optional[DocumentPlatform] = sb.field()

    @classmethod
    def from_orm(cls, orm: TeamOrm) -> "TeamGraphQLType":
        return TeamGraphQLType(
            id=orm.id,
            name=orm.name,
            document_platform=DocumentPlatform(value=orm.document_platform) if orm.document_platform else None,
        )

    @sb.field
    def github_repos(self) -> list[GithubRepoGraphQLType]:
        pass

    @sb.field
    def github_repos_feature_states_match(self) -> bool:
        pass

    @sb.field
    def github_installation(self) -> Optional[GithubInstallationGraphQLType]:
        pass

    @sb.field
    def atlassian_installation(self) -> Optional[AtlassianInstallationGraphQLType]:
        pass

    @sb.field
    def confluence_installation(self) -> Optional[ConnectInstallationGraphQLType]:
        pass

    @sb.field
    def jira_installation(self) -> Optional[ConnectInstallationGraphQLType]:
        pass

    @sb.field
    def slack_installation(self) -> Optional[SlackInstallationGraphQLType]:
        pass

    @sb.field
    def api_documentation_jobs(self) -> list[ApiDocumentationJobGraphQLType]:
        pass

    @sb.field
    def documents(self) -> list[DocumentSearchResultGraphQLType]:
        pass

    @sb.field
    def subscription(self) -> Optional[SubscriptionGraphQLType]:
        pass

    @sb.field
    def github_documents(self) -> list[GraphQLGithubDocumentGraphQLType]:
        pass