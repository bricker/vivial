"""
DEPRECATED: This module has been replaced by eave.stdlib.confluence_api.models
"""
from dataclasses import dataclass
from typing import Optional

from eave.stdlib.util import erasetype

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

    def __init__(self, data: JsonObject) -> None:
        self.id = erasetype(data, "id")
        self.name = erasetype(data, "name")
        self.url = erasetype(data, "url")
        self.scopes = erasetype(data, "scopes")
        self.avatarUrl = erasetype(data, "avatarUrl")


class ConfluenceUser:
    account_id: Optional[str] = None
    email: Optional[str] = None
    public_name: Optional[str] = None
    display_name: Optional[str] = None

    def __init__(self, data: JsonObject) -> None:
        self.account_id = erasetype(data, "accountId")
        self.email = erasetype(data, "email")
        self.public_name = erasetype(data, "publicName")
        self.display_name = erasetype(data, "displayName")
