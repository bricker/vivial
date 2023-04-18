from dataclasses import dataclass
from typing import List

import eave.stdlib.util as eave_util
import requests_oauthlib

from ..config import app_config
from .models import OauthFlowInfo


@dataclass
class AtlassianOAuthTokenResponse:
    access_token: str
    expires_in: int
    scope: str


@dataclass
class AtlassianAvailableResource:
    """
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/#implementing-oauth-2-0--3lo-
    """

    id: str
    name: str
    url: str
    scopes: List[str]
    avatarUrl: str


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

    def get_available_resources(self) -> list[AtlassianAvailableResource]:
        available_resources_response = self.request(
            method="GET",
            url="https://api.atlassian.com/oauth/token/accessible-resources",
        )
        available_resources_data: List[eave_util.JsonObject] = available_resources_response.json()
        available_resources = [AtlassianAvailableResource(**j) for j in available_resources_data]
        return available_resources

    def get_atlassian_cloud_id(self) -> str:
        available_resources = self.get_available_resources()
        assert len(available_resources) > 0
        return available_resources[0].id

    def oauth_flow_info(self) -> OauthFlowInfo:
        authorization_url, state = self.authorization_url()

        assert isinstance(authorization_url, str)
        assert isinstance(state, str)
        return OauthFlowInfo(authorization_url=authorization_url, state=state)
