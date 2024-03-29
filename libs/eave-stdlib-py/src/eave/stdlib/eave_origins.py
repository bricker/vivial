import enum


class EaveApp(enum.StrEnum):
    eave_api = "eave_api"
    eave_dashboard = "eave_dashboard"
    eave_metabase = "eave_metabase"
    eave_github_app = "eave_github_app"

    @property
    def appengine_name(self) -> str:
        match self:
            case EaveApp.eave_api:
                return "api"
            case EaveApp.eave_dashboard:
                return "www"
            case EaveApp.eave_github_app:
                return "github"
            case EaveApp.eave_metabase:
                return "metabase"


class ExternalOrigin(enum.StrEnum):
    github_api_client = "github_api_client"
