import asyncio
import re
from typing import Optional
from urllib.parse import urlparse
from pydantic import UUID4

import eave.stdlib.core_api.enums as enums
import eave.stdlib.core_api.models as eave_models
import eave.stdlib.github_api.client as github_api_client
import eave.stdlib.github_api.operations as gh_ops

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[enums.LinkType, list[str]] = {
    enums.LinkType.github: [
        r"github\.com",
        r"github\..+\.com",
    ],
}


def filter_supported_links(urls: list[str]) -> list[tuple[str, enums.LinkType]]:
    supported_links: list[tuple[str, enums.LinkType]] = []
    for link in urls:
        link_type = _get_link_type(link)
        if link_type:
            supported_links.append((link, link_type))
    return supported_links


async def map_url_content(eave_team_id: UUID4, urls: list[tuple[str, enums.LinkType]]) -> list[Optional[str]]:
    """
    Given a list of urls, returns mapping to content found at each link. Order is preserved.

    If an error is encountered while attempting to access the info at a link, the value at
    the position of the link in the returned list is None.
    """
    # gather content from all links in parallel
    tasks = []
    for link, link_type in urls:
        match link_type:
            case enums.LinkType.github:
                tasks.append(
                    asyncio.ensure_future(
                        github_api_client.get_file_content(
                            eave_team_id=eave_team_id,
                            input=gh_ops.GetGithubUrlContent.RequestBody(
                                eave_team_id=eave_team_id,
                                url=link,
                            ),
                        )
                    )
                )

    content_responses = await asyncio.gather(*tasks)
    content: list[Optional[str]] = content_responses
    return content


async def subscribe_to_file_changes(
    eave_team_id: UUID4, urls: list[tuple[str, enums.LinkType]]
) -> list[eave_models.Subscription]:
    """
    Create Eave Subscriptions to watch for changes in all of the URL resources in `urls`

    eave_team_id -- TeamOrm ID to create the subscription for
    urls -- links paired with their platform type [(url, url platform)]
    returns -- list of subscriptions that got created
    """
    tasks = []
    for link, link_type in urls:
        tasks.append(asyncio.ensure_future(_create_subscription_source(link, link_type, eave_team_id)))

    # have asyncio.gather eat any network exceptions an return them as part of result
    completed_tasks: list[Optional[eave_models.SubscriptionSource]] = await asyncio.gather(
        *tasks, return_exceptions=True
    )
    # only return the successful results
    subscription_sources = [src for src in completed_tasks if isinstance(src, eave_models.Subscription)]
    return subscription_sources


def _get_link_type(link: str) -> Optional[enums.LinkType]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns link type if supported, otherwise None
    """
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return link_type
    return None


async def _create_subscription_source(
    url: str, link_type: enums.LinkType, eave_team_id: UUID4
) -> Optional[eave_models.Subscription]:
    """
    Insert a subcription into the Eave database to watch the resource at `url`.

    url -- URL resource to create a subscription for watching
    link_type -- resource platform to subscribe on
    eave_team_id -- ID of team to associate subscription with
    """
    # populate required subscription data based on link type
    match link_type:
        case enums.LinkType.github:
            subscription_response = await github_api_client.create_subscription(
                eave_team_id=eave_team_id,
                input=gh_ops.CreateGithubResourceSubscription.RequestBody(
                    eave_team_id=eave_team_id,
                    url=url,
                ),
            )
            return subscription_response.subscription

    return None
