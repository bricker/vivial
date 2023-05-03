import typing
from dataclasses import dataclass
from functools import cache
from typing import List

import eave.stdlib
import requests_oauthlib
from oauthlib.oauth2 import OAuth2Token

from ..config import app_config
from .models import OAuthFlowInfo


@dataclass
class AtlassianOAuthTokenResponse:
    access_token: str
    expires_in: int
    scope: str


ATLASSIAN_OAUTH_SCOPES = [
    "write:confluence-content",
    "read:confluence-space.summary",
    "write:confluence-file",
    "read:confluence-props",
    "write:confluence-props",
    "read:confluence-content.all",
    "read:confluence-content.summary",
    "search:confluence",
    "read:confluence-content.permission",
    "read:confluence-user",
    "read:confluence-groups",
    "readonly:content.attachment:confluence",
    "read:jira-work",
    "read:jira-user",
    "write:jira-work",
    "read:me",
    "read:account",
    "offline_access",
]


class AtlassianOAuthSession(requests_oauthlib.OAuth2Session):
    def __init__(self, client=None, auto_refresh_kwargs=None, token=None, state=None, token_updater=None, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(
            client_id=app_config.eave_atlassian_app_client_id,
            redirect_uri=f"{app_config.eave_api_base}/oauth/atlassian/callback",
            scope=" ".join(ATLASSIAN_OAUTH_SCOPES),
            auto_refresh_url="https://auth.atlassian.com/oauth/token",
            client=client,
            auto_refresh_kwargs=auto_refresh_kwargs,
            token=token,
            state=state,
            token_updater=token_updater,
            **kwargs,
        )

    def authorization_url(self, state=None, **kwargs):  # type: ignore[no-untyped-def]
        return super().authorization_url(
            url="https://auth.atlassian.com/authorize",
            state=state,
            audience="api.atlassian.com",
            prompt="consent",
            **kwargs,
        )

    def fetch_token(self, code=None, authorization_response=None, body="", auth=None, username=None, password=None, method="POST", force_querystring=False, timeout=None, headers=None, verify=True, proxies=None, include_client_id=None, cert=None, **kwargs):  # type: ignore[no-untyped-def]
        return super().fetch_token(
            token_url="https://auth.atlassian.com/oauth/token",
            client_secret=app_config.eave_atlassian_app_client_secret,
            code=code,
            authorization_response=authorization_response,
            body=body,
            auth=auth,
            username=username,
            password=password,
            method=method,
            force_querystring=force_querystring,
            timeout=timeout,
            headers=headers,
            verify=verify,
            proxies=proxies,
            include_client_id=include_client_id,
            cert=cert,
            **kwargs,
        )

    def oauth_flow_info(self) -> OAuthFlowInfo:
        authorization_url, state = self.authorization_url()

        # for the typechecker:
        assert isinstance(authorization_url, str)
        assert isinstance(state, str)
        return OAuthFlowInfo(authorization_url=authorization_url, state=state)

    @cache
    def get_available_resources(self) -> List[eave.stdlib.atlassian.AtlassianAvailableResource]:
        available_resources_response = self.request(
            method="GET",
            url="https://api.atlassian.com/oauth/token/accessible-resources",
        )
        available_resources_data: List[eave.stdlib.util.JsonObject] = available_resources_response.json()
        available_resources = [eave.stdlib.atlassian.AtlassianAvailableResource(**j) for j in available_resources_data]
        return available_resources

    def get_userinfo(self) -> eave.stdlib.atlassian.ConfluenceUser:
        response = self.request(
            method="GET",
            url=f"{self.api_base_url}/rest/api/user/current",
        )

        response_json: eave.stdlib.util.JsonObject = response.json()
        userinfo = eave.stdlib.atlassian.ConfluenceUser(data=response_json, ctx=self.confluence_context)
        return userinfo

    @property
    def atlassian_cloud_id(self) -> str:
        available_resources = self.get_available_resources()
        assert len(available_resources) > 0
        id: str = available_resources[0].id
        return id

    @property
    def api_base_url(self) -> str:
        return f"https://api.atlassian.com/ex/confluence/{self.atlassian_cloud_id}"

    @property
    def confluence_context(self) -> eave.stdlib.atlassian.ConfluenceContext:
        return eave.stdlib.atlassian.ConfluenceContext(base_url=self.api_base_url)

    def get_token(self) -> OAuth2Token:
        """This is mostly for tests"""
        return typing.cast(OAuth2Token, self.token)
