import asyncio
import aiohttp
from typing import Optional, Any
import re
from urllib.parse import urlparse

import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.operations as operations
from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib import logger

from pydantic import UUID4


# TODO: does this whole file need translation to typescript for ts stdlib?

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[SupportedLink, list[str]] = {
    SupportedLink.github: [ # TODO: should these support www prefix?
        r"github\.com",
        r"github\..*\.com",
    ],
}


def is_supported_link(link: str) -> tuple[bool, Optional[SupportedLink]]:
    """
    Given a link, determine if we support parsing the content from that link.
    Returns tuple of (whether link is supported, link type if supported or None)
    """
    # check if link domain matches any supported link types
    # TODO: is domain matching too broad? should we compare against parts of path (like org/repo)?
    domain = urlparse(link).netloc
    for link_type, regex_patterns in SUPPORTED_LINKS.items():
        if any(re.match(pattern, domain) for pattern in regex_patterns):
            return (True, link_type)
    return (False, None)


# TODO: can we just pass in whole team object, or maybe better to limit it this way? if have whole team object, do we need to make request to get sources?
#    > TODO: we could possibly do that, but would require altering the TeamOrm and add nullable column(s) but thats ok? also need token access, not just linked platforms
async def get_link_content(team_id: UUID4, links: list[tuple[str, SupportedLink]]) -> list[str]:
    """
    Given a list of links, returns mapping to content found at each link.
    """
    # fetch from db what sources are connected, and the access token required to query their API
    # TODO: i feel like the oauth token is separate.. if gh repo is public, will providing unnecessary token mess w/ request?
    import os
    raw_sources = [{"type": SupportedLink.github, "token": os.getenv('GIT_TOKEN')}]
    # available_sources = await eave_core_api_client.get_available_sources(
    #     team_id=team_id,
    #     input=operations.GetAvailableSources.RequestBody(
    #         team=operations.TeamInput(id=team_id),
    #     ),
    # )
    # assert available_sources is not None
    source_tokens: dict[SupportedLink, str] = {source["type"]: source["token"] for source in raw_sources}

    # filter URLs to sites we support for ones the user has linked their eave account to
    # TODO: should eave only watch repos/code the user account owns/links directly? only anything in org/enterprise, or any link?
    accessible_links = [(link, link_type, source_tokens[link_type]) for link, link_type in links if link_type in source_tokens]

    # gather content from all links in parallel
    # TODO: worry about rate limit?
    tasks = []
    clients = {}
    for link, link_type, access_token in accessible_links:
        if link_type not in clients:
            clients[link_type] = _create_client(link_type, access_token)
        match link_type:
            case SupportedLink.github:
                tasks.append(asyncio.ensure_future(clients[link_type].request_file_content(link)))

    content_responses = await asyncio.gather(*tasks)
    content: list[str] = [resp.content for resp in content_responses]

    return content


# TODO: change SupportedLink type name???
def _create_client(client_type: SupportedLink, token: str) -> Any:
    match client_type:
        case SupportedLink.github:
            return GitHubClient(oauth_token=token)


# TODO move api clients to other file (this kinda isnt an api client anymore.. ?)
"""
gh link parser should be able to handle fetching file content from:
https://github.com/eave-fyi/eave-monorepo/blob/main/apps/github/package.json
https://github.com/eave-fyi/eave-monorepo/blob/bcr/2304/framework/apps/github/package.json
https://github.com/eave-fyi/eave-monorepo/blob/c840ee8d5d0ceb59ce00aeae3d553e2b16dbcfb9/apps/jira/package-lock.json
https://raw.githubusercontent.com/eave-fyi/eave-monorepo/bcr/2304/framework/apps/jira/package-lock.json?token=GHSAT0AAAAAAB4YW5GEFTJSSE5RUMVNPNB4ZCAVHLA
"""
class GitHubClient:
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token

        # mapping from github domain to API client for that domain
        # self._clients: dict[str, Github] = {}

    # TODO: worry about secret/oauth exfiltration if the link isnt actually a valid gh link?
    # (e.g. bad actor server logs request if they can get us to make req to github.bad-actor.com or somethign)
    async def request_file_content(self, url: str) -> Optional[str]:
        return await self._fetch_raw(url)
        # """
        # Fetch content of the file located at the URL `url`.
        # Returns None on GitHub API request failure
        # """
        # # build clients; will need a separate client for each different github domain
        # client = self._get_client(url)

        # # TODO: the gh link could hypothetically be one that our oauth token doesn't provide access to. should handle failures to fetch
        # # TODO what if it's not a file? what if dir? or repo? or line number permalink? or link is to non-default branch, possibly w/ slashes in branch name (messes up file path scrape)?
        # # should those be ignored (how?)? make recursive requests (expensive)? eat errors (if any)?
        # try:
        #     # TODO: the version of gh enterprise the company has could affect what endpoints are available
        #     # TODO: Use the .raw media type to retrieve the contents of the file.?
        #     # TODO: does pygithub suck ?
        #     res = await client.get_repo()

        #     return res
        # except Exception as error:
        #     logger.error(error)
        #     # gracefully recover from any errors that arise
        #     return None
 
    
    async def _fetch_raw(self, url: str) -> Optional[str]:
        """
        Fetch github file content from `url` using the raw.githubusercontent.com feature
        Returns None if `url` is not a path to a file (or if some other error was encountered).
        TODO: doesnt get us any closer to distinguishing branch name from file path in url; necessary for subscription??
        """
        # TODO: take session for optimizing call parallelism?
        # construct gh raw content url
        url_components = urlparse(url)
        content_location = url_components.path
        raw_url = ""
        # check if enterprise host
        if not re.match(r"github\.com", url_components.netloc):
            raw_url = f"https://{url_components.netloc}/raw"
        else:
            raw_url = "https://raw.githubusercontent.com"

        request_url = f"{raw_url}{content_location}"

        # attach auth token
        headers = {
            "Authorization": f"token {self.oauth_token}",
            "Accept": "application/vnd.github.v3.raw",
        }
        
        try:
            async with aiohttp.ClientSession() as http_session:
                resp = await http_session.request(
                    method="GET",
                    url=request_url,
                    headers=headers,
                )
                return await resp.text()
        except Exception as error:
            logger.error(error)
            # gracefully recover from any errors that arise
            return None


    # def _get_client(self, link: str) -> Github:
    #     """
    #     Get or build a GitHub API client that is compatible with the GitHub domain
    #     of the passed in URL.
    #     """
    #     domain = urlparse(link).netloc
    #     if domain not in self._clients:
    #         if domain == "github.com":
    #             self._clients[domain] = Github(self.oauth_token) # TODO: use login_or_token?
    #         else:
    #             # gh enterprise api URL is different
    #             base_url = f"https://{domain}/api/v3"
    #             self._clients[domain] = Github(login_or_token=self.oauth_token, base_url=base_url)

    #     return self._clients[domain]



