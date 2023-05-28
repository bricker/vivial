import enum


class AuthProvider(enum.StrEnum):
    google = "google"
    slack = "slack"
    atlassian = "atlassian"
    github = "github"


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


class Integration(enum.StrEnum):
    """
    Apps that a Team can integrate with.
    """

    slack = "slack"
    github = "github"
    forge = "forge"
    atlassian = "atlassian"


class LinkType(enum.StrEnum):
    """
    Link types that we support fetching content from for integration into AI documentation creation.
    """

    github = "github"

class EaveForgeInboundOperation(enum.StrEnum):
    createDocument = 'createDocument'
    updateDocument = 'updateDocument'
    archiveDocument = 'archiveDocument'
