import enum


class AuthProvider(enum.StrEnum):
    google = "google"
    slack = "slack"
    atlassian = "atlassian"


class DocumentPlatform(enum.StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"


class SubscriptionSourcePlatform(enum.StrEnum):
    slack = "slack"
    github = "github"
    jira = "jira"


class SubscriptionSourceEvent(enum.StrEnum):
    slack_message = "slack_message"
    github_file_change = "github_file_change"
    jira_issue_comment = "jira_issue_comment"