from typing import Any

from attr import dataclass
from eave.stdlib.core_api.enums import LinkType
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.github import GitHubClient


@dataclass
class LinkContext:
    url: str
    type: LinkType
    auth_data: Any  # TODO: perhaps not the best way to hold arbitrary auth data structures


def create_client(ctx: LinkContext) -> BaseClient:
    match ctx.type:
        case LinkType.github:
            installation_id = ctx.auth_data
            return GitHubClient(installation_id=installation_id)
