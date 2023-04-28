import asyncio
import re
from typing import Optional, Any, cast
from urllib.parse import urlparse
from .third_party_api_clients.github import GitHubClient
from pydantic import UUID4

import eave.stdlib.core_api.client as eave_core
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.util import create_client, LinkContext

# TODO: does this whole file need translation to typescript for ts stdlib? > yep

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[eave_models.SupportedLink, list[str]] = {
    eave_models.SupportedLink.github: [
        r"github\.com",
        r"github\..+\.com",
    ],
}

async def get_supported_links(urls: list[str]) -> list[tuple[str, eave_models.SupportedLink]]:
    supported_links: list[tuple[str, eave_models.SupportedLink]] = []
    for link in urls:
        link_type = _get_link_type(link)
        if link_type:
            supported_links.append((link, link_type))
    return supported_links
    

def _get_link_type(link: str) -> Optional[eave_models.SupportedLink]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns link type if supported, otherwise None
    """
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return link_type
    return None


async def get_link_content(team_id: UUID4, links: list[tuple[str, eave_models.SupportedLink]]) -> list[Optional[str]]:
    """
    Given a list of links, returns mapping to content found at each link. Order is preserved.

    If an error is encountered while attempting to access the info at a link, the value at
    the position of the link in the returned list is None.
    """
    contexts = await _get_link_auth_data(links)

    # gather content from all links in parallel
    tasks = []
    clients: dict[eave_models.SupportedLink, BaseClient] = {}
    for link_ctx in contexts:
        if link_ctx.type not in clients:
            clients[link_ctx.type] = create_client(link_ctx)
        match link_ctx.type:
            case eave_models.SupportedLink.github:
                tasks.append(asyncio.ensure_future(clients[link_ctx.type].get_file_content(link_ctx.url)))

    content_responses = await asyncio.gather(*tasks)
    content: list[Optional[str]] = content_responses

    for client in clients.values():
        await client.close()

    return content

async def subscribe(eave_team_id: UUID4, urls: list[str]) -> None:
    # TODO: cleanup
    contexts = await _get_link_auth_data(urls)

    tasks = []
    clients: dict[eave_models.SupportedLink, BaseClient] = {}
    for link_ctx in contexts:
        if link_ctx.type not in clients:
            clients[link_ctx.type] = create_client(link_ctx)
        tasks.append(asyncio.ensure_future(_helper(clients[link_ctx.type], link_ctx.url, link_ctx.type, eave_team_id)))
    
    await asyncio.gather(*tasks)

# TODO: only take 1 link?
# TODO: rename
async def _get_link_auth_data(links: list[str]) -> list[LinkContext]:
    # fetch from core_api what sources are connected, and the access token required to query their API
    # TODO: waiting for Byran's endpoint to be implemented
    raw_sources = [{"type": eave_models.SupportedLink.github, "app_id": "todo", "installation_id": "todo"}]
    # available_sources = await eave_core_api_client.get_available_sources(
    #     team_id=team_id,
    #     input=operations.GetAvailableSources.RequestBody(
    #         team=operations.TeamInput(id=team_id),
    #     ),
    # )
    # assert available_sources is not None
    source_tokens: dict[eave_models.SupportedLink, tuple[str, str]] = {
        source["type"]: (source["app_id"], source["installation_id"]) for source in raw_sources
    }

    # filter URLs to sites we support for ones the user has linked their eave account to
    accessible_links = [
        LinkContext(url=link, type=link_type, auth_data=source_tokens[link_type]) for link, link_type in links if link_type in source_tokens
    ]
    return accessible_links

# TODO: base clinet doesnt work becauase we need gh specific funcitons...
#TODO: rename
async def _helper(untyped_client: Any, link: str, link_type: eave_models.SupportedLink, eave_team_id: UUID4) -> None:
    """
    does a thing
    """
    source_id: Optional[str] = None

    # populate source_id based on link type
    match link_type:
        case eave_models.SupportedLink.github:
            client: GitHubClient = cast(GitHubClient, untyped_client)
            # fetch unique info about repo to build subscription source ID
            repo_info = await client.get_repo(link)
            path_chunks = link.split(repo_info.full_name)
            if len(path_chunks) < 2:
                return
            blob_path = path_chunks[1] #TODO: this still starts wtih /blob/
            source_id = f"{repo_info.node_id}#{blob_path}"

    if source_id:
        await eave_core.create_subscription(
            team_id=eave_team_id,
            input=eave_ops.CreateSubscription.RequestBody(
                subscription=eave_ops.SubscriptionInput(
                    source=eave_models.SubscriptionSource(
                        platform=eave.stdlib.core_api.enums.SubscriptionSourcePlatform.github,
                        event=eave.stdlib.core_api.enums.SubscriptionSourceEvent.github_file_change,
                        id=source_id,
                    )
                ),
            ),
        )