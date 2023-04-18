import asyncio
import aiohttp
import enum
from typing import Optional
import re
from urllib.parse import urlparse
import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.operations as operations
from pydantic import UUID4


class SupportedLink(enum.Enum):
    """link types that we support fetching content from"""

    github = "github"


# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[SupportedLink, list[str]] = {
    SupportedLink.github: [r"(www.)?github.*\.com"],
}


def is_supported_link(link: str) -> tuple[bool, Optional[SupportedLink]]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns tuple of (whether link is supported, link type if supported or None)
    """
    # check if link domain matches any supported link types
    # TODO: is domain matching too broad? perhaps only for github/source code....
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return (True, link_type)
    return (False, None)


# TODO update type to accept SupportedLink for each link (list[tuple[str, SupportedLink]])? easier to determine accessible_links
# TODO: can we just pass in whole team object, or maybe better to limit it this way? if have whole team object, do we need to make request to get sources?
async def get_link_content(team_id: UUID4, links: list[str]) -> list[str]:
    """
    Given a list of links, returns mapping to content found at each link.
    """
    # TODO: should i be trying to make this general enough to work for any link potentioaly?
    # TODO: fetch from db what soureces are connected
    available_sources = await eave_core_api_client.get_available_sources(
        team_id=team_id,
        input=operations.GetAvailableSources.RequestBody(
            team=operations.TeamInput(id=team_id),
        ),
    )
    # TODO: should eave only watch repos/code the user account owns/links directly? only anything in org/enterprise, or any link?
    accessible_links: list[str] = list(filter(lambda x: is_link_of_type(available_sources, x), links))

    # TODO: the gh link could hypothetically be one that our oauth token doesn't provide access to. should handle failures to fetch
    # TODO: fetch all at once like here https://www.twilio.com/blog/asynchronous-http-requests-in-python-with-aiohttp
    async with aiohttp.ClientSession() as session:
        tasks = []
        for link, link_type in accessible_links:
            match link_type:
                case SupportedLink.github:
                    # TODO what if it's not a file? what if dir? or repo? just ignore those for now?
                    tasks.append(asyncio.ensure_future(GitHubClient.request_file_content(link, session)))

    content_responses = await asyncio.gather(*tasks)
    content: list[str] = [resp.content for resp in content_responses]

    return content


# TODO move api clients to other file???
# TODO: PyGitHub api client requires enterprise specific base_url (e.g. github.enterprise.com/api/v3 if is enterprise)
class GitHubClient:
    pass
