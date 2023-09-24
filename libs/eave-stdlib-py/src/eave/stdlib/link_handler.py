import asyncio
import enum
import re
from typing import Optional
from urllib.parse import urlparse
from pydantic import UUID4

from eave.stdlib.github_api.operations.content import GetGithubUrlContent
from eave.stdlib.github_api.operations.subscriptions import CreateGithubResourceSubscription

from .core_api.models.subscriptions import SubscriptionInfo

from .eave_origins import EaveApp

class LinkType(enum.StrEnum):
    """
    Link types that we support fetching content from for integration into AI documentation creation.
    """

    github = "github"

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[LinkType, list[str]] = {
    LinkType.github: [
        r"github\.com",
        r"github\..+\.com",
    ],
}


def filter_supported_links(urls: list[str]) -> list[tuple[str, LinkType]]:
    supported_links: list[tuple[str, LinkType]] = []
    for link in urls:
        link_type = _get_link_type(link)
        if link_type:
            supported_links.append((link, link_type))
    return supported_links


async def map_url_content(
    origin: EaveApp, eave_team_id: UUID4, urls: list[tuple[str, LinkType]]
) -> list[Optional[str]]:
    """
    Given a list of urls, returns mapping to content found at each link. Order is preserved.

    If an error is encountered while attempting to access the info at a link, the value at
    the position of the link in the returned list is None.
    """
    # gather content from all links in parallel
    tasks: list[asyncio.Task[GetGithubUrlContent.ResponseBody]] = []
    for link, link_type in urls:
        match link_type:
            case LinkType.github:
                tasks.append(
                    asyncio.ensure_future(
                        GetGithubUrlContent.perform(
                            origin=origin,
                            team_id=eave_team_id,
                            input=GetGithubUrlContent.RequestBody(
                                url=link,
                            ),
                        )
                    )
                )

    content_responses: list[Optional[GetGithubUrlContent.ResponseBody]] = await asyncio.gather(*tasks)
    content = list(map(lambda x: x.content if x else None, content_responses))
    return content


async def subscribe_to_file_changes(
    origin: EaveApp, eave_team_id: UUID4, urls: list[tuple[str, LinkType]]
) -> list[SubscriptionInfo]:
    """
    Create Eave Subscriptions to watch for changes in all of the URL resources in `urls`

    eave_team_id -- TeamOrm ID to create the subscription for
    urls -- links paired with their platform type [(url, url platform)]
    returns -- list of subscriptions that got created
    """
    tasks: list[asyncio.Task[Optional[SubscriptionInfo] | Exception]] = []
    for link, link_type in urls:
        tasks.append(
            asyncio.ensure_future(
                _create_subscription_source(origin=origin, url=link, link_type=link_type, eave_team_id=eave_team_id)
            )
        )

    # have asyncio.gather eat any network exceptions and return them as part of result
    completed_tasks: list[Optional[SubscriptionInfo]] = await asyncio.gather(*tasks, return_exceptions=True)
    # only return the successful results
    subscription_sources = [src for src in completed_tasks if type(src) is SubscriptionInfo]
    return subscription_sources


def _get_link_type(link: str) -> Optional[LinkType]:
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
    origin: EaveApp, url: str, link_type: LinkType, eave_team_id: UUID4
) -> Optional[SubscriptionInfo]:
    """
    Insert a subcription into the Eave database to watch the resource at `url`.

    url -- URL resource to create a subscription for watching
    link_type -- resource platform to subscribe on
    eave_team_id -- ID of team to associate subscription with
    """
    # populate required subscription data based on link type
    match link_type:
        case LinkType.github:
            subscription_response = await CreateGithubResourceSubscription.perform(
                origin=origin,
                team_id=eave_team_id,
                input=CreateGithubResourceSubscription.RequestBody(
                    url=url,
                ),
            )
            return SubscriptionInfo(
                subscription=subscription_response.subscription,
                document_reference=subscription_response.document_reference,
            )

    return None
