import asyncio
import re
from typing import Any, Optional, cast
from urllib.parse import urlparse
import base64

import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.enums
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.core_api.operations as eave_ops
from eave.stdlib.core_api.models import LinkType
from eave.stdlib.third_party_api_clients.base import BaseClient
from eave.stdlib.third_party_api_clients.util import LinkContext, create_client
from pydantic import UUID4

from .logging import logger
from .third_party_api_clients.github import GitHubClient

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[eave_models.LinkType, list[str]] = {
    eave_models.LinkType.github: [
        r"github\.com",
        r"github\..+\.com",
    ],
}


def filter_supported_links(urls: list[str]) -> list[tuple[str, eave_models.LinkType]]:
    supported_links: list[tuple[str, eave_models.LinkType]] = []
    for link in urls:
        link_type = _get_link_type(link)
        if link_type:
            supported_links.append((link, link_type))
    return supported_links


async def map_url_content(eave_team_id: UUID4, urls: list[tuple[str, eave_models.LinkType]]) -> list[Optional[str]]:
    """
    Given a list of urls, returns mapping to content found at each link. Order is preserved.

    If an error is encountered while attempting to access the info at a link, the value at
    the position of the link in the returned list is None.
    """
    contexts = await _build_link_contexts(eave_team_id, urls)

    # gather content from all links in parallel
    tasks = []
    clients: dict[eave_models.LinkType, BaseClient] = {}
    for link_ctx in contexts:
        if link_ctx.type not in clients:
            clients[link_ctx.type] = create_client(link_ctx)
        match link_ctx.type:
            case eave_models.LinkType.github:
                tasks.append(asyncio.ensure_future(clients[link_ctx.type].get_file_content(link_ctx.url)))

    content_responses = await asyncio.gather(*tasks)
    content: list[Optional[str]] = content_responses

    for client in clients.values():
        await client.close()

    return content


async def subscribe(eave_team_id: UUID4, urls: list[tuple[str, eave_models.LinkType]]) -> None:
    """
    Create Eave Subscriptions to watch for changes in all of the URL resources in `urls`

    eave_team_id -- TeamOrm ID to create the subscription for
    urls -- links paired with their platform type [(url, url platform)]
    """
    contexts = await _build_link_contexts(eave_team_id, urls)

    tasks = set()
    clients: dict[eave_models.LinkType, BaseClient] = {}
    for link_ctx in contexts:
        if link_ctx.type not in clients:
            clients[link_ctx.type] = create_client(link_ctx)
        # create fire and forget bg task
        task = asyncio.create_task(
            _create_subscription(clients[link_ctx.type], link_ctx.url, link_ctx.type, eave_team_id)
        )
        # add to set to hold strong ref to prevent task being garbo collected
        tasks.add(task)
        # cleanup reference on task completion
        task.add_done_callback(tasks.discard)


def _get_link_type(link: str) -> Optional[eave_models.LinkType]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns link type if supported, otherwise None
    """
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return link_type
    return None


async def _build_link_contexts(eave_team_id: UUID4, links: list[tuple[str, eave_models.LinkType]]) -> list[LinkContext]:
    """
    Given a collection of links and an Eave TeamOrm ID, return the data
    required to authenticate with the 3rd party API for each link.
    If the Eave Team is not integrated with platform the link is from,
    that link is filtered out of the returned list, as the Team account
    has not explicitly given us permission to attempt to read data from
    those links.

    eave_team_id -- ID of the Eave TeamOrm to fetch platform integrations from
    links -- list of links to build API client auth data for
    """
    # fetch from core_api what sources are connected, and the auth data required to query their API
    team_response = await eave_core_api_client.get_team(
        team_id=eave_team_id,
    )

    api_client_auth_data: dict[LinkType, str] = {}
    for supported_type in LinkType:
        match supported_type:
            case LinkType.github:
                if gh_integration := team_response.integrations.github:
                    api_client_auth_data[LinkType.github] = gh_integration.github_install_id
            case _:
                logger.error("Unexpected SupportedLink type encountered while building link auth context")

    # filter URLs to platforms the user has linked their eave account to
    accessible_links = [
        LinkContext(url=link, type=link_type, auth_data=api_client_auth_data[link_type])
        for link, link_type in links
        if link_type in api_client_auth_data
    ]
    return accessible_links


async def _create_subscription(
    untyped_client: Any, url: str, link_type: eave_models.LinkType, eave_team_id: UUID4
) -> None:
    """
    Insert a subcription to watch the resource at `url` into the Eave database.

    untyped_client -- API client corresponding to `link_type` for fetching data to build subscription with
    url -- URL resource to create a subscription for watching
    link_type -- resource platform to subscribe on
    eave_team_id -- ID of team to associate subscription with
    """
    source_id: Optional[str] = None
    platform: Optional[eave.stdlib.core_api.enums.SubscriptionSourcePlatform] = None
    event: Optional[eave.stdlib.core_api.enums.SubscriptionSourceEvent] = None

    # populate required subscription data based on link type
    match link_type:
        case eave_models.LinkType.github:
            client: GitHubClient = cast(GitHubClient, untyped_client)
            # fetch unique info about repo to build subscription source ID
            repo_info = await client.get_repo(url)
            path_chunks = url.split(f"{repo_info.full_name}/blob/")
            # we need the 2nd element, which is branch name + resource path
            if len(path_chunks) < 2:
                return
            blob_path = path_chunks[1]
            # b64 encode since our chosen ID delimiter '#' is a valid character in file paths and branch names
            encoded_blob_path = base64.b64encode(blob_path.encode()).decode()
            source_id = f"{repo_info.node_id}#{encoded_blob_path}"
            platform = eave.stdlib.core_api.enums.SubscriptionSourcePlatform.github
            event = eave.stdlib.core_api.enums.SubscriptionSourceEvent.github_file_change

    assert (
        source_id is not None and platform is not None and event is not None
    ), "Subscription creation data not fully populated"
    
    await eave_core_api_client.create_subscription(
        team_id=eave_team_id,
        input=eave_ops.CreateSubscription.RequestBody(
            subscription=eave_ops.SubscriptionInput(
                source=eave_models.SubscriptionSource(
                    platform=platform,
                    event=event,
                    id=source_id,
                )
            ),
        ),
    )
