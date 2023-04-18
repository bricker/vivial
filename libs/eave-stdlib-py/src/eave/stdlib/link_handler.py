import enum
from typing import Optional
import re
from urllib.parse import urlparse
import eave.stdlib.core_api.client as eave_core_api_client


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


# TODO update type to accept SupportedLink for each link?
async def get_link_content(links: list[str]) -> list[str]:
    """
    Given a list of links, returns mapping to content found at each link.
    """
    # TODO: should i be trying to make this general enough to work for any link potentioaly?
    # TODO: fetch from db what soureces are connected. coreapi request?
    available_sources = await eave_core_api_client.get_code_sources()
    # TODO: take note of enterprise paths; cant rely on public domain name pattern
    # TODO: should eave only watch repos/code the user account owns/links directly? only anything in org/enterprise, or any link?
    accessible_source_links: list[str] = list(filter(lambda x: is_prefix_of(available_sources, x), links))

    # TODO contact source code api of the linked source hubs. coreapi request??
    # TODO: the gh link could hypothetically be one that our oauth token doesn't provide access to. should handle failures to fetch
    source_text = await eave_core_api_client.get_source_code(accessible_source_links)
    return links

# TODO move to other file???

class GitHubClient:
    pass