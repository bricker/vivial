import asyncio
import aiohttp
from typing import Optional, Any, Self
import re
from urllib.parse import urlparse
from attr import dataclass

import eave.stdlib.core_api.client as eave_core_api_client
import eave.stdlib.core_api.operations as operations
from eave.stdlib.core_api.models import SupportedLink
from eave.stdlib import logger

from pydantic import UUID4

# TODO: does this whole file need translation to typescript for ts stdlib?

# mapping from link type to regex for matching raw links against
SUPPORTED_LINKS: dict[SupportedLink, list[str]] = {
    SupportedLink.github: [  # TODO: should these support www prefix?
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
    # TODO: is oauth token compatible w/ gh api auth?.. if gh repo is public, will providing unnecessary token mess w/ request?
    import os

    raw_sources = [{"type": SupportedLink.github, "token": os.getenv("GIT_TOKEN")}]
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
    accessible_links = [
        (link, link_type, source_tokens[link_type]) for link, link_type in links if link_type in source_tokens
    ]

    # gather content from all links in parallel
    # TODO: worry about rate limit when making many calls in parallel?
    tasks = []
    clients: dict[SupportedLink, BaseClient] = {}
    for link, link_type, access_token in accessible_links:
        if link_type not in clients:
            clients[link_type] = _create_client(link_type, access_token)
        match link_type:
            case SupportedLink.github:
                tasks.append(asyncio.ensure_future(clients[link_type].get_file_content(link)))

    content_responses = await asyncio.gather(*tasks)
    print(content_responses)  # DEBGU
    # TODO: get actual content from resp
    content: list[str] = [resp.content for resp in content_responses]

    for client in clients.values():
        await client.close()

    return content


# TODO: change SupportedLink type name???
def _create_client(client_type: SupportedLink, token: str) -> Any:
    match client_type:
        case SupportedLink.github:
            return GitHubClient(oauth_token=token)


# TODO move api clients to other file


@dataclass
class GithubRepository:
    default_branch: str
    # contents_url: str

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> "GithubRepository":
        # strip unexpected keys from response input
        class_fields = set(cls.__annotations__.keys())
        clean_response = {k: v for k, v in response.items() if k in class_fields}
        # pour cleaned kv pairs into dataclass init
        return GithubRepository(**clean_response)


class BaseClient:
    async def get_file_content(self, url: str) -> Optional[str]:
        pass

    async def close(self) -> None:
        pass


"""
gh link parser should be able to handle fetching file content from:
https://github.com/eave-fyi/eave-monorepo/blob/main/apps/github/package.json
https://github.com/eave-fyi/eave-monorepo/blob/bcr/2304/framework/apps/github/package.json
https://github.com/eave-fyi/eave-monorepo/blob/c840ee8d5d0ceb59ce00aeae3d553e2b16dbcfb9/apps/jira/package-lock.json
https://raw.githubusercontent.com/eave-fyi/eave-monorepo/bcr/2304/framework/apps/jira/package-lock.json?token=GHSAT0AAAAAAB4YW5GEFTJSSE5RUMVNPNB4ZCAVHLA
"""


class GitHubClient(BaseClient):
    def __init__(self, oauth_token: str):
        self.oauth_token = oauth_token

        # mapping from github domain to session with auth headers for that domain
        self._sessions: dict[str, aiohttp.ClientSession] = {}
        self._repo_info: Optional[GithubRepository] = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, exc_tb: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """
        Must be called to close client sessions
        """
        for client in self._sessions.values():
            await client.close()

    async def get_file_path(self, url: str) -> Optional[str]:
        """
        Get the file path from a GitHub URL, if the URL points to the repo's default branch.
        If the URL points to any branch that isn't the default branch, returns None.

        TODO: this still suffers from inability to know which part of URL is branch name. e.g. this would return incorrect file path for a branch named <default branch name>/extension
        """
        # TODO: support non-default branches; perform a search through all remote branches to find longest match after blob
        _, url_path = url.split("/blob/")

        # get default branch name from API
        try:
            default_branch = (await self._get_repo(url)).default_branch

            if re.match(rf"{default_branch}.*", url_path):
                # chop the branch name + '/' off the front of URL path to get file path w/o leading '/'
                return url_path[len(default_branch) + 1 :]
        except Exception as error:
            # either url was not pointing to a repo, or error during api call
            logger.error(error)

        return None

    async def get_file_content(self, url: str) -> Optional[str]:
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

    def _get_repo_location(self, url: str) -> tuple[str, str]:
        """
        Parse the GitHub org name and repo name from the input `url`
        Returns (org, repo)
        """
        # split path from url
        url_path_components = urlparse(url).path.split("/")

        if len(url_path_components) < 3:
            raise Exception(f"GitHub URL {url} did not contain expected org and repo name in its path")

        # url_path_components == ['', 'org', 'repo', ...]
        return (url_path_components[1], url_path_components[2])

    async def _get_repo(self, url: str) -> GithubRepository:
        """
        Request data about the github repo pointed to by `url` from the GitHub API
        """
        # TODO: cache result based on repo location? {org/repo : resp}
        client = self._get_session(url)

        # gather data for API request URL
        org, repo = self._get_repo_location(url)

        # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        async with client.get(f"/repos/{org}/{repo}") as resp:
            json_resp = await resp.json()
            return GithubRepository.from_response(json_resp)

    async def _fetch_raw(self, url: str) -> Optional[str]:
        """
        Fetch github file content from `url` using the raw.githubusercontent.com feature
        Returns None if `url` is not a path to a file (or if some other error was encountered).
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

    def _get_session(self, link: str) -> aiohttp.ClientSession:
        """
        Get or build a aiohttp.ClientSession prepared with the necessary headers
        for with the GitHub API of the passed in URL.
        (enterprise and public github have different API base URLs)
        """
        domain = urlparse(link).netloc
        if domain not in self._sessions:
            # TODO: will our app oauth token actually work as bearer here?
            self._sessions[domain] = aiohttp.ClientSession(
                # base url is different for enterprise apis
                base_url="https://api.github.com" if domain == "github.com" else f"https://{domain}/api/v3",
                headers={
                    "Accept": "application/vnd.github+json",
                    "Authorization": f"Bearer {self.oauth_token}",
                    "X-GitHub-Api-Version": "2022-11-28",
                },
            )

        return self._sessions[domain]
