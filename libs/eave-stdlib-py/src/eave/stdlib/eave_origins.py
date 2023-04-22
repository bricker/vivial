import enum


class EaveOrigin(enum.Enum):
    eave_api = "api"
    eave_www = "www"
    eave_github_app = "github_app"
    eave_slack_app = "slack_app"
    eave_atlassian_app = "atlassian_app"
