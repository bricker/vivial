from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.github import GitHubClient


# TODO: undoubtedly this interface will evolve as more clients get added
def create_client(client_type: SupportedLink, app_id: str, installation_id: str) -> BaseClient:
    match client_type:
        case SupportedLink.github:
            return GitHubClient(app_id=app_id, installation_id=installation_id)
