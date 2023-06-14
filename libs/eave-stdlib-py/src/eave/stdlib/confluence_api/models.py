import enum
from typing import Optional

from pydantic import BaseModel, Field
from eave.stdlib.core_api.models import BaseInputModel

from eave.stdlib.typing import JsonObject


class ConfluenceSearchParamsInput(BaseInputModel):
    space_key: Optional[str]
    text: str


class UpdateContentInput(BaseInputModel):
    id: str
    body: str


class DeleteContentInput(BaseInputModel):
    content_id: str


class AtlassianAvailableResource(BaseModel):
    """
    https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/#implementing-oauth-2-0--3lo-
    """

    id: Optional[str]
    name: Optional[str]
    url: Optional[str]
    scopes: Optional[list[str]]
    avatarUrl: Optional[str]


class ConfluenceSpaceType(enum.StrEnum):
    global_ = "global"
    personal = "personal"


class ConfluenceSpaceStatus(enum.StrEnum):
    current = "current"
    archived = "archived"


class ConfluenceContentType(enum.StrEnum):
    page = "page"
    blogpost = "blogpost"
    custom = "custom"
    attachment = "attachment"


class ConfluenceContentStatus(enum.StrEnum):
    current = "current"
    draft = "draft"


class BodyType(BaseModel):
    representation: str
    value: str


class ConfluenceSpaceDescription(BaseModel):
    plain: BodyType
    view: BodyType


class ConfluenceSpace(BaseModel):
    id: str | int  # https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-905
    key: str
    name: str
    type: ConfluenceSpaceType
    status: ConfluenceSpaceStatus
    homepageId: Optional[str | int]  # https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-905
    description: Optional[ConfluenceSpaceDescription]


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


class ConfluenceGenericLinks(BaseModel):
    base: Optional[str]
    self: Optional[str]
    tinyui: Optional[str]
    editui: Optional[str]
    webui: Optional[str]
    context: Optional[str]
    collection: Optional[str]


class ApiResource:
    expandable: Optional[JsonObject]
    links: Optional[ConfluenceGenericLinks]


class ConfluencePageVersion(BaseModel):
    pass


class ConfluenceOperationCheckResult(BaseModel):
    pass


class ConfluenceUserIcon(BaseModel):
    pass


class ConfluenceUserDetails(BaseModel):
    pass


class ConfluenceUser(BaseModel):
    type: Optional[ConfluenceUserType]
    accountType: Optional[ConfluenceUserAccountType]
    details: Optional[ConfluenceUserDetails]
    isExternalCollaborator: Optional[bool]
    externalCollaborator: Optional[bool]
    username: Optional[str]
    userKey: Optional[str]
    accountId: Optional[str]
    email: Optional[str]
    publicName: Optional[str]
    displayName: Optional[str]
    timeZone: Optional[str]
    profilePicture: Optional[ConfluenceUserIcon]
    operations: Optional[list[ConfluenceOperationCheckResult]]
    personalSpace: Optional[ConfluenceSpace]


class ConfluenceUsersUserKeys(BaseModel):
    users: Optional[list[ConfluenceUser]]
    userKeys: Optional[list[str]]


class ConfluencePageContributors(BaseModel):
    publishers: Optional[ConfluenceUsersUserKeys]


class ConfluencePageHistory(BaseModel):
    latest: Optional[bool]
    contributors: Optional[ConfluencePageContributors]
    createdDate: Optional[str]
    createdBy: Optional[ConfluenceUser]
    ownedBy: Optional[ConfluenceUser]
    lastUpdated: Optional[ConfluencePageVersion]
    previousVersion: Optional[ConfluencePageVersion]
    nextVersion: Optional[ConfluencePageVersion]


class ConfluenceMediaToken(BaseModel):
    collectionIds: Optional[list[str]]
    contentId: Optional[str]
    expiryDateTime: Optional[str]
    fileIds: Optional[list[str]]
    token: Optional[str]


class ConfluenceWebResourceDependencies(BaseModel):
    pass


class ConfluenceEmbeddable(BaseModel):
    pass


class ConfluenceEmbeddedContent(BaseModel):
    entityId: Optional[int]
    entityType: Optional[str]
    entity: Optional[ConfluenceEmbeddable]


class ConfluenceContentBody(BaseModel):
    value: Optional[str]
    representation: Optional[ConfluenceContentBodyRepresentation]
    embeddedContent: Optional[list[ConfluenceEmbeddedContent]]
    mediaToken: Optional[ConfluenceMediaToken]
    webresource: Optional[ConfluenceWebResourceDependencies]


class ConfluencePageBody(BaseModel):
    storage: Optional[ConfluenceContentBody]


class ConfluencePage(BaseModel):
    id: str
    status: str
    title: str
    type: Optional[str]
    macroRenderedOutput: Optional[JsonObject]
    extensions: Optional[JsonObject]
    ancestors: Optional[list[JsonObject]]
    container: Optional[JsonObject]
    body: Optional[ConfluencePageBody]
    space: Optional[ConfluenceSpace]
    history: Optional[ConfluencePageHistory]
    version: Optional[ConfluencePageVersion]
    links: Optional[ConfluenceGenericLinks] = Field(alias="_links")

    @property
    def url(self) -> str:
        if self.links and self.links.base and self.links.webui:
            return "".join([self.links.base, self.links.webui])
        else:
            return ""


class ContainerSummary(BaseModel):
    title: str
    displayUrl: str


class Breadcrumb(BaseModel):
    label: str
    url: str
    separator: str


class ConfluenceSearchResultWithBody(BaseModel):
    id: Optional[str | int]
    type: Optional[str]
    status: Optional[ConfluenceContentStatus]
    title: Optional[str]
    body: ConfluencePageBody
    links: Optional[ConfluenceGenericLinks] = Field(alias="_links")
    # These properties are documented in Confluence API docs but never actually returned...?
    # content: Optional[ConfluencePage]
    # user: Optional[ConfluenceUser]
    # space: Optional[ConfluenceSpace]
    # excerpt: Optional[str]
    # resultParentContainer: Optional[ContainerSummary]
    # resultGlobalContainer: Optional[ContainerSummary]
    # breadcrumbs: Optional[list[Breadcrumb]]
    # entityType: Optional[str]
    # iconCssClass: Optional[str]
    # lastModified: Optional[str]
    # friendlyLastModified: Optional[str]
    # score: Optional[int]
