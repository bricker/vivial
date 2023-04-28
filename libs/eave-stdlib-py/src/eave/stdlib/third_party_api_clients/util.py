from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.github import GitHubClient


def create_client(client_type: SupportedLink, token: str) -> BaseClient:
    match client_type:
        case SupportedLink.github:
            return GitHubClient(oauth_token=token)
