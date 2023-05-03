"""
Atlassian data models
"""
import enum
import typing
from dataclasses import dataclass
from typing import Optional

from . import util


@dataclass
class AtlassianAvailableResource:
    """
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/#implementing-oauth-2-0--3lo-
    """

    id: str
    name: str
    url: str
    scopes: typing.List[str]
    avatarUrl: str


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
    self_: str
    base_url: str
    tinyui: Optional[str] = None
    editui: Optional[str] = None
    webui: Optional[str] = None
    context: Optional[str] = None
    collection: Optional[str] = None

    # FIXME: According to the Confluence documentation, "_links" might be a string (instead of an object)
    def __init__(self, data: dict[str, str], ctx: ConfluenceContext) -> None:
        self.base_url = ctx.base_url
        self.self_ = data["self"]
        self.tinyui = data.get("tinyui")
        self.editui = data.get("editui")
        self.webui = data.get("webui")
        self.context = data.get("context")
        self.collection = data.get("collection")

    @property
    def editui_url(self) -> Optional[str]:
        if self.editui is None:
            return None

        return self.base_url + "/wiki" + self.editui

    @property
    def webui_url(self) -> Optional[str]:
        if self.webui is None:
            return None

        return self.base_url + "/wiki" + self.webui

    @property
    def tinyui_url(self) -> Optional[str]:
        if self.tinyui is None:
            return None

        return self.base_url + "/wiki" + self.tinyui


class ConfluenceBaseModel:
    _data: util.JsonObject
    expandable: Optional[util.JsonObject] = None
    links: Optional[ConfluenceGenericLinks] = None

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        self._data = data

        if (links := data.get("_links")) is not None:
            self.links = ConfluenceGenericLinks(links, ctx)

        if (expandable := data.get("_expandable")) is not None:
            self.expandable = expandable

    @property
    def canonical_url(self) -> Optional[str]:
        if self.links is not None and self.links.tinyui_url is not None:
            return self.links.tinyui_url
        else:
            return None


class ConfluencePageVersion(ConfluenceBaseModel):
    pass


class ConfluenceOperationCheckResult(ConfluenceBaseModel):
    pass


class ConfluenceUserIcon(ConfluenceBaseModel):
    pass


class ConfluenceSpace(ConfluenceBaseModel):
    id: Optional[int]
    key: Optional[str]
    name: Optional[str]

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)
        self.id = data.get("id")
        self.key = data.get("key")
        self.name = data.get("name")


class ConfluenceUserDetails(ConfluenceBaseModel):
    pass


class ConfluenceUser(ConfluenceBaseModel):
    type_: ConfluenceUserType
    account_type: ConfluenceUserAccountType
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

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.type_ = ConfluenceUserType(value=data["type"])
        self.account_type = ConfluenceUserAccountType(value=data["accountType"])
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
            self.details = ConfluenceUserDetails(details, ctx)

        if (profile_picture := data.get("profilePicture")) is not None:
            self.profile_picture = ConfluenceUserIcon(profile_picture, ctx)

        if (operations := data.get("operations")) is not None:
            self.operations = [ConfluenceOperationCheckResult(operation, ctx) for operation in operations]

        if (personal_space := data.get("personalSpace")) is not None:
            self.personal_space = ConfluenceSpace(personal_space, ctx)


class ConfluenceUsersUserKeys(ConfluenceBaseModel):
    users: list[ConfluenceUser]
    user_keys: list[str]

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.users = data["users"]
        self.user_keys = data["userKeys"]


class ConfluencePageContributors(ConfluenceBaseModel):
    publishers: Optional[ConfluenceUsersUserKeys] = None

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        if (publishers := data.get("publishers")) is not None:
            self.publishers = ConfluenceUsersUserKeys(publishers, ctx)


class ConfluencePageHistory(ConfluenceBaseModel):
    latest: bool
    created_date: str
    contributors: Optional[ConfluencePageContributors] = None
    created_by: Optional[ConfluenceUser] = None
    owned_by: Optional[ConfluenceUser] = None
    last_updated: Optional[ConfluencePageVersion] = None
    previous_version: Optional[ConfluencePageVersion] = None
    next_version: Optional[ConfluencePageVersion] = None

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.latest = data["latest"]
        self.created_date = data["createdDate"]

        if (contributors := data.get("contributors")) is not None:
            self.contributors = ConfluencePageContributors(contributors, ctx)

        if (created_by := data.get("createdBy")) is not None:
            self.created_by = ConfluenceUser(created_by, ctx)

        if (owned_by := data.get("ownedBy")) is not None:
            self.owned_by = ConfluenceUser(owned_by, ctx)

        if (last_updated := data.get("lastUpdated")) is not None:
            self.last_updated = ConfluencePageVersion(last_updated, ctx)

        if (previous_version := data.get("previousVersion")) is not None:
            self.previous_version = ConfluencePageVersion(previous_version, ctx)

        if (next_version := data.get("nextVersion")) is not None:
            self.next_version = ConfluencePageVersion(next_version, ctx)


class ConfluenceMediaToken(ConfluenceBaseModel):
    collection_ids: list[str]
    content_id: str
    expiry_date_time: str
    file_ids: list[str]
    token: str

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.collection_ids = data["collectionIds"]
        self.content_id = data["contentId"]
        self.expiry_date_time = data["expiryDateTime"]
        self.file_ids = data["fileIds"]
        self.token = data["token"]


class ConfluenceWebResourceDependencies(ConfluenceBaseModel):
    pass


class ConfluenceEmbeddable(ConfluenceBaseModel):
    pass


class ConfluenceEmbeddedContent(ConfluenceBaseModel):
    entity_id: int
    entity_type: str
    entity: ConfluenceEmbeddable

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.entity_id = data["entityId"]
        self.entity_type = data["entityType"]
        self.entity = ConfluenceEmbeddable(data["entity"], ctx)


class ConfluenceContentBody(ConfluenceBaseModel):
    value: str
    representation: ConfluenceContentBodyRepresentation
    embedded_content: list[ConfluenceEmbeddedContent]
    media_token: Optional[ConfluenceMediaToken] = None
    webresource: Optional[ConfluenceWebResourceDependencies] = None

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.value = data["value"]
        self.representation = ConfluenceContentBodyRepresentation(value=data["representation"])
        self.embedded_content = [
            ConfluenceEmbeddedContent(embedded_content, ctx) for embedded_content in data["embeddedContent"]
        ]

        if (media_token := data.get("mediaToken")) is not None:
            self.media_token = ConfluenceMediaToken(media_token, ctx)

        if (webresource := data.get("webresource")) is not None:
            self.webresource = ConfluenceWebResourceDependencies(webresource, ctx)


class ConfluencePageBody(ConfluenceBaseModel):
    content: Optional[ConfluenceContentBody] = None
    representation: ConfluenceContentBodyRepresentation = ConfluenceContentBodyRepresentation._unknown

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        if (content := data.get(ConfluenceContentBodyRepresentation.view.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.view

        if (content := data.get(ConfluenceContentBodyRepresentation.export_view.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.export_view

        if (content := data.get(ConfluenceContentBodyRepresentation.styled_view.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.styled_view

        if (content := data.get(ConfluenceContentBodyRepresentation.storage.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.storage

        if (content := data.get(ConfluenceContentBodyRepresentation.wiki.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.wiki

        if (content := data.get(ConfluenceContentBodyRepresentation.editor.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.editor

        if (content := data.get(ConfluenceContentBodyRepresentation.editor2.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.editor2

        if (content := data.get(ConfluenceContentBodyRepresentation.anonymous_export_view.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.anonymous_export_view

        if (content := data.get(ConfluenceContentBodyRepresentation.atlas_doc_format.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.atlas_doc_format

        if (content := data.get(ConfluenceContentBodyRepresentation.dynamic.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.dynamic

        if (content := data.get(ConfluenceContentBodyRepresentation.raw.value)) is not None:
            self.content = ConfluenceContentBody(content, ctx)
            self.representation = ConfluenceContentBodyRepresentation.raw


class ConfluencePage(ConfluenceBaseModel):
    ctx: ConfluenceContext
    id: str
    type: str
    status: str
    title: str
    macro_rendered_output: util.JsonObject
    extensions: util.JsonObject
    ancestors: Optional[list[util.JsonObject]] = None
    container: Optional[util.JsonObject] = None
    body: Optional[ConfluencePageBody] = None
    space: Optional[ConfluenceSpace] = None
    history: Optional[ConfluencePageHistory] = None
    version: Optional[ConfluencePageVersion] = None

    def __init__(self, data: util.JsonObject, ctx: ConfluenceContext) -> None:
        super().__init__(data, ctx)

        self.id = data["id"]
        self.type = data["type"]
        self.status = data["status"]
        self.title = data["title"]
        self.macro_rendered_output = data["macroRenderedOutput"]
        self.extensions = data["extensions"]
        self.ancestors = data.get("ancestors")
        self.container = data.get("container")

        if (body := data.get("body")) is not None:
            self.body = ConfluencePageBody(body, ctx)

        if (space := data.get("space")) is not None:
            self.space = ConfluenceSpace(space, ctx)

        if (history := data.get("history")) is not None:
            self.history = ConfluencePageHistory(history, ctx)

        if (version := data.get("version")) is not None:
            self.version = ConfluencePageVersion(version, ctx)
