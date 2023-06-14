"""
DEPRECATED: This module has been replaced by eave.stdlib.confluence_api.models
"""
from dataclasses import dataclass
from typing import Optional, cast

from .typing import JsonObject


@dataclass
class AtlassianAvailableResource:
    """
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/#implementing-oauth-2-0--3lo-
    """

    id: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    scopes: Optional[list[str]] = None
    avatarUrl: Optional[str] = None


class ConfluenceUser:
    account_id: Optional[str] = None
    email: Optional[str] = None
    public_name: Optional[str] = None
    display_name: Optional[str] = None

    def __init__(self, data: JsonObject) -> None:
        self.account_id = cast(str | None, data.get("accountId"))
        self.email = cast(str | None, data.get("email"))
        self.public_name = cast(str | None, data.get("publicName"))
        self.display_name = cast(str | None, data.get("displayName"))
