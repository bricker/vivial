import strawberry.federation as sb

@sb.type
class Integrations:
    github_integration: Optional[GithubInstallation] = sb.field(default=None)
    slack_integration: Optional[SlackInstallation] = sb.field(default=None)
    atlassian_integration: Optional[AtlassianInstallation] = sb.field(default=None)
    confluence_integration: Optional[ConnectInstallation] = sb.field(default=None)
    jira_integration: Optional[ConnectInstallation] = sb.field(default=None)
