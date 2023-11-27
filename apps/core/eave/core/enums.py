from enum import StrEnum
import strawberry.federation as sb

@sb.enum
class DocumentPlatform(StrEnum):
    eave = "eave"
    confluence = "confluence"
    google_drive = "google_drive"

@sb.enum
class AuthProvider(StrEnum):
    google = "google"
    slack = "slack"
    atlassian = "atlassian"
    github = "github"


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

@sb.enum
class Integration(StrEnum):
    """
    Apps that a Team can integrate with.
    """

    slack = "slack"
    github = "github"
    atlassian = "atlassian"
    confluence = "confluence"
    jira = "jira"

@sb.enum
class AtlassianProduct(StrEnum):
    jira = "jira"
    confluence = "confluence"
