from typing import Any

from attr import dataclass
from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.github import GitHubClient


# TODO: move data type to shared loc?
@dataclass
class LinkContext:
    url: str
    type: SupportedLink
    auth_data: Any  # TODO: perhaps not the best way to hold arbitrary auth data structures


def create_client(ctx: LinkContext) -> BaseClient:
    match ctx.type:
        case SupportedLink.github:
            app_id, installation_id = ctx.auth_data
            return GitHubClient(app_id=app_id, installation_id=installation_id)
