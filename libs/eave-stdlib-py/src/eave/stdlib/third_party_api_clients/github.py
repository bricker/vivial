import re
from typing import Any, Optional, Self
from urllib.parse import urlparse

import aiohttp
import eave.stdlib.eave_origins as eave_origins
import eave.stdlib.jwt as eave_jwt
import eave.stdlib.signing as eave_signing
from attr import dataclass
from eave.stdlib import logger
from eave.stdlib.third_party_api_clients.base import BaseClient

# TODO: move to better location?
GITHUB_APP_ID: str = "300560"


# TODO: moved to shared loc?
@dataclass
class GithubRepository:
    """
    Source response object defined in Github API
    https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
    """

    node_id: str
    full_name: str

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> "GithubRepository":
        """
        Given a JSON object decoded to a python dict, extract only the
        fields defined by `GithubRepository` dataclass, and construct a new instance.
        """
        # strip unexpected keys from response input
        class_fields = set(cls.__annotations__.keys())
        clean_response = {k: v for k, v in response.items() if k in class_fields}
        # pour cleaned kv pairs into dataclass init
        return GithubRepository(**clean_response)


@dataclass
class GithubInstallationAccessToken:
    """
    Source response object defined in Github API
    https://docs.github.com/en/rest/apps/apps?apiVersion=2022-11-28#create-an-installation-access-token-for-an-app
    """

    token: str
    expires_at: str

    @classmethod
    def from_response(cls, response: dict[str, Any]) -> "GithubInstallationAccessToken":
        """
        Given a JSON object decoded to a python dict, extract only the
        fields defined by `GithubInstallationAccessToken` dataclass, and construct a new instance.
        """
        # strip unexpected keys from response input
        class_fields = set(cls.__annotations__.keys())
        clean_response = {k: v for k, v in response.items() if k in class_fields}
        # pour cleaned kv pairs into dataclass init
        return GithubInstallationAccessToken(**clean_response)


class GitHubClient(BaseClient):
    def __init__(self, installation_id: str):
        self.access_token: Optional[str] = None
        self.app_id = GITHUB_APP_ID
        self.installation_id = installation_id

        # mapping from github domain to session with auth headers for that domain
        self._sessions: dict[str, aiohttp.ClientSession] = {}

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

    async def get_file_content(self, url: str) -> Optional[str]:
        """
        Fetch content of the file located at the URL `url`.
        Returns None on GitHub API request failure
        """
        try:
            return await self._fetch_raw(url)
        except Exception as error:
            logger.error(error)
            # gracefully recover from any errors that arise
            return None

    async def get_repo(self, url: str) -> GithubRepository:
        """
        Request data about the github repo pointed to by `url` from the GitHub API
        (`url` doesnt have to point directly to the repo, it can point to any file w/in the repo too)
        """
        client = await self._get_session(url)

        # gather data for API request URL
        org, repo = self._get_repo_location(url)

        # https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
        async with client.get(f"/repos/{org}/{repo}") as resp:
            json_resp = await resp.json()
            return GithubRepository.from_response(json_resp)

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

    async def _fetch_raw(self, url: str) -> Optional[str]:
        """
        Fetch github file content from `url` using the raw.githubusercontent.com feature
        Returns None if `url` is not a path to a file (or if some other error was encountered).

        NOTE: raw.githubusercontent.com is ratelimitted by IP, not requesting user, so this wont scale far
        https://github.com/github/docs/issues/8031#issuecomment-881427112
        """
        # construct gh raw content url
        url_components = urlparse(url)
        # remove blob from URL because raw content URLs dont have it
        content_location = url_components.path.replace("blob/", "")
        raw_url = ""
        # check if enterprise host
        if not re.match(r"github\.com", url_components.netloc):
            raw_url = f"https://{url_components.netloc}/raw"
        else:
            raw_url = "https://raw.githubusercontent.com"

        request_url = f"{raw_url}{content_location}"

        # request/set auth token
        await self._set_installation_token(
            app_id=self.app_id,
            installation_id=self.installation_id,
            url=url,
        )
        assert self.access_token

        # attach auth token
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3.raw",
        }

        async with aiohttp.ClientSession() as http_session:
            resp = await http_session.request(
                method="GET",
                url=request_url,
                headers=headers,
            )
            file_content = await resp.text()

            # gh returns 404 text if no raw content at URL path
            if file_content == "404: Not Found":
                return None
            return file_content

    async def _get_session(self, link: str) -> aiohttp.ClientSession:
        """
        Get or build a aiohttp.ClientSession prepared with the necessary headers
        for with the GitHub API of the passed in URL.
        If a new ClientSession is built, it is locally cached for later use.
        """
        domain = urlparse(link).netloc
        if domain not in self._sessions:
            await self._set_installation_token(
                app_id=self.app_id,
                installation_id=self.installation_id,
                url=link,
            )
            assert self.access_token
            self._sessions[domain] = self._create_session(domain=domain, token=self.access_token)

        return self._sessions[domain]

    def _create_session(self, domain: str, token: str) -> aiohttp.ClientSession:
        """
        Build a aiohttp.ClientSession prepared with the necessary headers
        for with the GitHub API of the passed in domain.
        (enterprise and public github have different API base URLs)
        """
        return aiohttp.ClientSession(
            # base url is different for enterprise apis
            base_url="https://api.github.com" if domain == "github.com" else f"https://{domain}/api/v3",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )

    def _create_jwt(self, app_id: str) -> str:
        """
        Create a JWT for authenticating as a GitHub App to request an installation token
        https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app

        app_id -- ID of the GitHub App to authenticate as
        returns the created JWT string
        """
        signing_key = eave_signing.get_key(eave_origins.ExternalOrigin.github_api_client.value)
        jwt = eave_jwt.create_jwt(
            signing_key=signing_key,
            purpose=eave_jwt.JWTPurpose.access,
            iss=app_id,
            aud="", # these claim fields are not needed for gh JWT, it's ok to leave them empty 
            sub="",
        )
        jwt_str: str = jwt.to_str()
        return jwt_str

    async def _set_installation_token(self, app_id: str, installation_id: str, url: str) -> str:
        """
        Create an installation token for the app identified by `app_id`
        that can authenticate with the GitHub API required to access the
        resource at `url`.
        The created installation token is then set in `self.access_token`.

        app_id -- ID of the GitHub App to authenticate through
        installation_id -- ID of the installation to authenticate as
        url -- resource the installation token should be able to access
        returns the created access token after saving it in `self.access_token`
        """
        if self.access_token:
            # token has already been set
            return self.access_token

        # temporarily set auth token as JWT so we can auth as app
        jwt_token = self._create_jwt(app_id)
        # request installation access token.
        # create 1-time-use client with JWT auth
        client = self._create_session(domain=urlparse(url).netloc, token=jwt_token)

        async with client.post(f"/app/installations/{installation_id}/access_tokens") as token_resp:
            token_json: dict[str, Any] = await token_resp.json()
            token_data = GithubInstallationAccessToken.from_response(token_json)
            self.access_token = token_data.token

        await client.close()
        return self.access_token
