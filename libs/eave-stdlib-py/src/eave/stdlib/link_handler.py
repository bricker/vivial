import asyncio
from typing import Optional, Any
import re
from urllib.parse import urlparse

from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.util import create_client


from pydantic import UUID4

# TODO: does this whole file need translation to typescript for ts stdlib?

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[SupportedLink, list[str]] = {
    SupportedLink.github: [
        r"github\.com",
        r"github\..+\.com",
    ],
}


def is_supported_link(link: str) -> tuple[bool, Optional[SupportedLink]]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns tuple of (whether link is supported, link type if supported or None)
    """
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return (True, link_type)
    return (False, None)


async def get_link_content(team_id: UUID4, links: list[tuple[str, SupportedLink]]) -> list[Optional[str]]:
    """
    Given a list of links, returns mapping to content found at each link. Order is preserved.

    If an error is encountered while attempting to access the info at a link, the value at
    the position of the link in the returned list is None.
    """
    # fetch from db what sources are connected, and the access token required to query their API
    # TODO: waiting for Byran's endpoint to be implemented
    raw_sources = [{"type": SupportedLink.github, "app_id": "todo", "installation_id": "todo"}]
    # available_sources = await eave_core_api_client.get_available_sources(
    #     team_id=team_id,
    #     input=operations.GetAvailableSources.RequestBody(
    #         team=operations.TeamInput(id=team_id),
    #     ),
    # )
    # assert available_sources is not None
    source_tokens: dict[SupportedLink, tuple[str, str]] = {source["type"]: (source["app_id"], source["installation_id"]) for source in raw_sources}

    # filter URLs to sites we support for ones the user has linked their eave account to
    accessible_links = [
        (link, link_type, source_tokens[link_type]) for link, link_type in links if link_type in source_tokens
    ]

    # gather content from all links in parallel
    tasks = []
    clients: dict[SupportedLink, BaseClient] = {}
    for link, link_type, (app_id, installation_id) in accessible_links:
        if link_type not in clients:
            clients[link_type] = create_client(client_type=link_type, app_id=app_id, installation_id=installation_id)
        match link_type:
            case SupportedLink.github:
                tasks.append(asyncio.ensure_future(clients[link_type].get_file_content(link)))

    content_responses = await asyncio.gather(*tasks)
    content: list[Optional[str]] = content_responses

    for client in clients.values():
        await client.close()

    return content
