"""
Atlassian data models
"""
import enum
from dataclasses import dataclass
from typing import Optional

from .typing import JsonObject
from . import logging


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


class ConfluenceUserType(enum.Enum):
    known = "known"
    unknown = "unknown"
    anonymous = "anonymous"
    user = "user"


class ConfluenceUserAccountType(enum.Enum):
    atlassian = "atlassian"
    app = "app"
    unavailable = ""


class ConfluenceContentBodyRepresentation(enum.Enum):
    view = "view"
    export_view = "export_view"
    styled_view = "styled_view"
    storage = "storage"
    editor = "editor"
    editor2 = "editor2"
    anonymous_export_view = "anonymous_export_view"
    wiki = "wiki"
    atlas_doc_format = "atlas_doc_format"
    dynamic = "dynamic"
    raw = "raw"
    _unknown = "_unknown"


@dataclass
class ConfluenceContext:
    base_url: str


class ConfluenceGenericLinks:
    base: Optional[str] = None
    self_: Optional[str] = None
    tinyui: Optional[str] = None
    editui: Optional[str] = None
    webui: Optional[str] = None
    context: Optional[str] = None
    collection: Optional[str] = None

    # FIXME: According to the Confluence documentation, "_links" might be a string (instead of an object)
    def __init__(self, data: dict[str, str]) -> None:
        self.base = data.get("base")
        self.self_ = data.get("self")
        self.tinyui = data.get("tinyui")
        self.editui = data.get("editui")
        self.webui = data.get("webui")
        self.context = data.get("context")
        self.collection = data.get("collection")


class ConfluenceBaseModel:
    _data: JsonObject
    expandable: Optional[JsonObject] = None
    links: Optional[ConfluenceGenericLinks] = None

    def __init__(self, data: JsonObject) -> None:
        self._data = data

        if (links := data.get("_links")) is not None:
            self.links = ConfluenceGenericLinks(links)

        if (expandable := data.get("_expandable")) is not None:
            self.expandable = expandable

    def canonical_url(self, base_url: str) -> str:
        if self.links is None:
            logging.eaveLogger.warning("confluence content._links missing")
            return base_url

        path = self.links.tinyui or self.links.webui
        if path is None:
            logging.eaveLogger.warning("confluence content._links missing tinyui and webui")
            return base_url

        # Path is prefixed with a slash already
        return f"{base_url}/wiki{path}"


class ConfluencePageVersion(ConfluenceBaseModel):
    pass


class ConfluenceOperationCheckResult(ConfluenceBaseModel):
    pass


class ConfluenceUserIcon(ConfluenceBaseModel):
    pass


class ConfluenceSpace(ConfluenceBaseModel):
    id: Optional[int] = None
    key: Optional[str] = None
    name: Optional[str] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)
        self.id = data.get("id")
        self.key = data.get("key")
        self.name = data.get("name")


class ConfluenceUserDetails(ConfluenceBaseModel):
    pass


class ConfluenceUser(ConfluenceBaseModel):
    type_: Optional[ConfluenceUserType] = None
    account_type: Optional[ConfluenceUserAccountType] = None
    details: Optional[ConfluenceUserDetails] = None
    is_external_collaborator: Optional[bool] = None
    external_collaborator: Optional[bool] = None
    username: Optional[str] = None
    user_key: Optional[str] = None
    account_id: Optional[str] = None
    email: Optional[str] = None
    public_name: Optional[str] = None
    display_name: Optional[str] = None
    time_zone: Optional[str] = None
    profile_picture: Optional[ConfluenceUserIcon] = None
    operations: Optional[list[ConfluenceOperationCheckResult]] = None
    personal_space: Optional[ConfluenceSpace] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        if (type_ := data.get("type")) is not None:
            self.type_ = ConfluenceUserType(value=type_)

        if (account_type := data.get("accountType")) is not None:
            self.account_type = ConfluenceUserAccountType(value=account_type)

        self.is_external_collaborator = data.get("isExternalCollaborator")
        self.external_collaborator = data.get("externalCollaborator")
        self.username = data.get("username")
        self.user_key = data.get("userKey")
        self.account_id = data.get("accountId")
        self.email = data.get("email")
        self.public_name = data.get("publicName")
        self.display_name = data.get("displayName")
        self.time_zone = data.get("timeZone")

        if (details := data.get("details")) is not None:
            self.details = ConfluenceUserDetails(details)

        if (profile_picture := data.get("profilePicture")) is not None:
            self.profile_picture = ConfluenceUserIcon(profile_picture)

        if (operations := data.get("operations")) is not None:
            self.operations = [ConfluenceOperationCheckResult(operation) for operation in operations]

        if (personal_space := data.get("personalSpace")) is not None:
            self.personal_space = ConfluenceSpace(personal_space)


class ConfluenceUsersUserKeys(ConfluenceBaseModel):
    users: Optional[list[ConfluenceUser]] = None
    user_keys: Optional[list[str]] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.users = data.get("users")
        self.user_keys = data.get("userKeys")


class ConfluencePageContributors(ConfluenceBaseModel):
    publishers: Optional[ConfluenceUsersUserKeys] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        if (publishers := data.get("publishers")) is not None:
            self.publishers = ConfluenceUsersUserKeys(publishers)


class ConfluencePageHistory(ConfluenceBaseModel):
    latest: Optional[bool] = None
    created_date: Optional[str] = None
    contributors: Optional[ConfluencePageContributors] = None
    created_by: Optional[ConfluenceUser] = None
    owned_by: Optional[ConfluenceUser] = None
    last_updated: Optional[ConfluencePageVersion] = None
    previous_version: Optional[ConfluencePageVersion] = None
    next_version: Optional[ConfluencePageVersion] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.latest = data.get("latest")
        self.created_date = data.get("createdDate")

        if (contributors := data.get("contributors")) is not None:
            self.contributors = ConfluencePageContributors(contributors)

        if (created_by := data.get("createdBy")) is not None:
            self.created_by = ConfluenceUser(created_by)

        if (owned_by := data.get("ownedBy")) is not None:
            self.owned_by = ConfluenceUser(owned_by)

        if (last_updated := data.get("lastUpdated")) is not None:
            self.last_updated = ConfluencePageVersion(last_updated)

        if (previous_version := data.get("previousVersion")) is not None:
            self.previous_version = ConfluencePageVersion(previous_version)

        if (next_version := data.get("nextVersion")) is not None:
            self.next_version = ConfluencePageVersion(next_version)


class ConfluenceMediaToken(ConfluenceBaseModel):
    collection_ids: Optional[list[str]] = None
    content_id: Optional[str] = None
    expiry_date_time: Optional[str] = None
    file_ids: Optional[list[str]] = None
    token: Optional[str] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.collection_ids = data.get("collectionIds")
        self.content_id = data.get("contentId")
        self.expiry_date_time = data.get("expiryDateTime")
        self.file_ids = data.get("fileIds")
        self.token = data.get("token")


class ConfluenceWebResourceDependencies(ConfluenceBaseModel):
    pass


class ConfluenceEmbeddable(ConfluenceBaseModel):
    pass


class ConfluenceEmbeddedContent(ConfluenceBaseModel):
    entity_id: Optional[int] = None
    entity_type: Optional[str] = None
    entity: Optional[ConfluenceEmbeddable] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.entity_id = data.get("entityId")
        self.entity_type = data.get("entityType")

        if (entity := data.get("entity")) is not None:
            self.entity = ConfluenceEmbeddable(entity)


class ConfluenceContentBody(ConfluenceBaseModel):
    value: Optional[str] = None
    representation: Optional[ConfluenceContentBodyRepresentation] = None
    embedded_content: Optional[list[ConfluenceEmbeddedContent]] = None
    media_token: Optional[ConfluenceMediaToken] = None
    webresource: Optional[ConfluenceWebResourceDependencies] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.value = data.get("value")

        if (repr := data.get("representation")) is not None:
            self.representation = ConfluenceContentBodyRepresentation(value=repr)

        if (embc := data.get("embeddedContent")) is not None:
            self.embedded_content = [ConfluenceEmbeddedContent(embedded_content) for embedded_content in embc]

        if (media_token := data.get("mediaToken")) is not None:
            self.media_token = ConfluenceMediaToken(media_token)

        if (webresource := data.get("webresource")) is not None:
            self.webresource = ConfluenceWebResourceDependencies(webresource)


class ConfluencePageBody(ConfluenceBaseModel):
    content: Optional[ConfluenceContentBody] = None
    representation: ConfluenceContentBodyRepresentation = ConfluenceContentBodyRepresentation._unknown

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        if (content := data.get(ConfluenceContentBodyRepresentation.view.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.view

        if (content := data.get(ConfluenceContentBodyRepresentation.export_view.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.export_view

        if (content := data.get(ConfluenceContentBodyRepresentation.styled_view.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.styled_view

        if (content := data.get(ConfluenceContentBodyRepresentation.storage.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.storage

        if (content := data.get(ConfluenceContentBodyRepresentation.wiki.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.wiki

        if (content := data.get(ConfluenceContentBodyRepresentation.editor.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.editor

        if (content := data.get(ConfluenceContentBodyRepresentation.editor2.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.editor2

        if (content := data.get(ConfluenceContentBodyRepresentation.anonymous_export_view.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.anonymous_export_view

        if (content := data.get(ConfluenceContentBodyRepresentation.atlas_doc_format.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.atlas_doc_format

        if (content := data.get(ConfluenceContentBodyRepresentation.dynamic.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.dynamic

        if (content := data.get(ConfluenceContentBodyRepresentation.raw.value)) is not None:
            self.content = ConfluenceContentBody(content)
            self.representation = ConfluenceContentBodyRepresentation.raw


class ConfluencePage(ConfluenceBaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    title: Optional[str] = None
    macro_rendered_output: Optional[JsonObject] = None
    extensions: Optional[JsonObject] = None
    ancestors: Optional[list[JsonObject]] = None
    container: Optional[JsonObject] = None
    body: Optional[ConfluencePageBody] = None
    space: Optional[ConfluenceSpace] = None
    history: Optional[ConfluencePageHistory] = None
    version: Optional[ConfluencePageVersion] = None

    def __init__(self, data: JsonObject) -> None:
        super().__init__(data)

        self.id = data.get("id")
        self.type = data.get("type")
        self.status = data.get("status")
        self.title = data.get("title")
        self.macro_rendered_output = data.get("macroRenderedOutput")
        self.extensions = data.get("extensions")
        self.ancestors = data.get("ancestors")
        self.container = data.get("container")

        if (body := data.get("body")) is not None:
            self.body = ConfluencePageBody(body)

        if (space := data.get("space")) is not None:
            self.space = ConfluenceSpace(space)

        if (history := data.get("history")) is not None:
            self.history = ConfluencePageHistory(history)

        if (version := data.get("version")) is not None:
            self.version = ConfluencePageVersion(version)
