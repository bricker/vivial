import enum


class EaveOrigin(enum.StrEnum):
    eave_api = "eave_api"
    eave_www = "eave_www"
    eave_github_app = "eave_github_app"
    eave_slack_app = "eave_slack_app"
    eave_atlassian_app = "eave_atlassian_app"
    eave_jira_app = "eave_jira_app"
    eave_confluence_app = "eave_confluence_app"


class ExternalOrigin(enum.StrEnum):
    github_api_client = "github_api_client"
