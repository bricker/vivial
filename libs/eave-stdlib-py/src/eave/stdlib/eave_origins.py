import enum


class EaveApp(enum.StrEnum):
    eave_api = "eave_api"
    eave_dashboard = "eave_dashboard"
    eave_metabase = "eave_metabase"


class ExternalOrigin(enum.StrEnum):
    github_api_client = "github_api_client"
