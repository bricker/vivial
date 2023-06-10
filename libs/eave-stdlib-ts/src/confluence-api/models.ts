import { JsonObject } from '../types.js';

export interface PaginatedResults<T> {
  start?: number;
  limit?: number;
  size?: number;
  results: T[];
}

export interface ConfluenceSearchParamsInput {
  space_key?: string;
  text: string;
}

export interface DeleteContentInput {
  content_id: string;
}

export enum ConfluenceOperation {
  administer = 'administer',
  archive = 'archive',
  clear_permissions = 'clear_permissions',
  copy = 'copy',
  create = 'create',
  create_space = 'create_space',
  delete = 'delete',
  export = 'export',
  move = 'move',
  purge = 'purge',
  purge_version = 'purge_version',
  read = 'read',
  restore = 'restore',
  restrict_content = 'restrict_content',
  update = 'update',
  use = 'use',
}

export enum ConfluenceSpaceType {
  global = 'global',
  personal = 'personal',
}

export enum ConfluenceSpaceStatus {
  current = 'current',
  archived = 'archived',
}


export enum ConfluenceContentType {
  page = 'page',
  blogpost = 'blogpost',
  custom = 'custom',
}

/* https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-spacekey-content-type-get-request-Query%20parameters */
export enum ConfluenceSpaceContentDepth {
  root = 'root',
  all = 'all',
}

export enum ConfluenceUserType {
  known = 'known',
  unknown = 'unknown',
  anonymous = 'anonymous',
  user = 'user',
}

export enum ConfluenceUserAccountType {
  atlassian = 'atlassian',
  app = 'app',
  unavailable = '',
}

export enum ConfluenceContentBodyRepresentation {
  view = 'view',
  export_view = 'export_view',
  styled_view = 'styled_view',
  storage = 'storage',
  editor = 'editor',
  editor2 = 'editor2',
  anonymous_export_view = 'anonymous_export_view',
  wiki = 'wiki',
  atlas_doc_format = 'atlas_doc_format',
  dynamic = 'dynamic',
  raw = 'raw',
  _unknown = '_unknown',
}

export enum ConfluenceContentStatus {
  current = 'current',
  draft = 'draft',
}

export enum ConfluenceGroupType {
  group = 'group',
}

export interface BodyType {
  representation: string;
  value: string;
}

export interface ConfluenceSpaceDescription {
  plain: BodyType;
  view: BodyType;
}

export interface ConfluenceLabel {
  prefix?: string;
  name?: string;
  id?: string;
  label?: string;
}

export interface ConfluenceSpaceMetadata {
  labels?: PaginatedResults<ConfluenceLabel>;
  _links: ConfluenceGenericLinks;
}
export interface ConfluenceSpaceIcon {
  path?: string;
  width?: string;
  height?: string;
  isDefault?: boolean;
}

export interface ConfluenceOperationCheckResult {
  operation?: ConfluenceOperation;
  targetType?: string;
}

export interface ConfluenceSpacePermission {
  id: number;
  subjects?: {
    user?: PaginatedResults<ConfluenceUser>;
    group?: PaginatedResults<ConfluenceGroup>;
  };
  operation?: ConfluenceOperationCheckResult;
  anonymousAccess?: boolean;
  unlicensedAccess?: boolean;
}

export interface ConfluenceSpaceSettingsEditor {
  page?: string;
  blogpost?: string;
  default?: string;
}

export interface ConfluenceSpaceSettings {
  routeOverrideEnabled?: boolean;
  editor?: ConfluenceSpaceSettingsEditor;
  spaceKey?: string;
}

export interface ConfluenceSpaceTheme {
  themeKey?: string;
  name?: string;
  description?: string;
  icon?: ConfluenceSpaceIcon;
}

export interface ConfluenceSpaceLookAndFeelColors {
  backgroundColor?: string;
  color?: string;
}
export interface ConfluenceSpaceNavigationLookAndFeel {
  color?: string;
  highlightColor?: string;
  hoverOrFocus?: ConfluenceSpaceLookAndFeelColors;
}

export interface ConfluenceSpaceBackgroundLookAndFeel {
  background?: string;
  backgroundAttachment?: string;
  backgroundBlendMode?: string;
  backgroundClip?: string;
  backgroundColor?: string;
  backgroundImage?: string;
  backgroundOrigin?: string;
  backgroundPosition?: string;
  backgroundRepeat?: string;
  backgroundSize?: string;
}

export interface ConfluenceSpaceContainerLookAndFeel extends ConfluenceSpaceBackgroundLookAndFeel {
  padding?: string;
  borderRadius?: string;
}

export interface ConfluenceSpaceScreenLookAndFeel extends ConfluenceSpaceBackgroundLookAndFeel {
  layer?: object;
  gutterTop?: string;
  gutterRight?: string;
  gutterBottom?: string;
  gutterLeft?: string;
}

export interface ConfluenceSpaceLookAndFeel {
  headings?: {
    color?: string;
  };
  links?: {
    color?: string;
  };
  menus?: {
    color?: string;
    hoverOrFocus?: ConfluenceSpaceLookAndFeelColors;
  };
  header?: {
    backgroundColor?: string;
    button?: ConfluenceSpaceLookAndFeelColors;
    primaryNavigation?: ConfluenceSpaceNavigationLookAndFeel;
    secondaryNavigation?: ConfluenceSpaceNavigationLookAndFeel;
    search?: ConfluenceSpaceLookAndFeelColors;
  };
  horizontalHeader?: {
    backgroundColor?: string;
    button?: ConfluenceSpaceLookAndFeelColors;
    primaryNavigation?: ConfluenceSpaceNavigationLookAndFeel;
    secondaryNavigation?: ConfluenceSpaceNavigationLookAndFeel;
    search?: ConfluenceSpaceLookAndFeelColors;
  };
  content?: {
    screen?: ConfluenceSpaceScreenLookAndFeel;
    container?: ConfluenceSpaceContainerLookAndFeel;
    header?: ConfluenceSpaceContainerLookAndFeel;
    body?: ConfluenceSpaceContainerLookAndFeel;
  };
  bordersAndDividers?: {
    color?: string;
  };
  spaceReference?: object; // Schema not documented
}

export interface ConfluenceSpaceHistory {
  createdDate?: string; // Atlassian says "date-time" format, whatever that means
  createdBy?: ConfluenceUser;
}

export interface ConfluenceSpace {
  id: string | number; // https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-905
  key: string;
  name: string;
  type: ConfluenceSpaceType;
  status: ConfluenceSpaceStatus;
  description?: ConfluenceSpaceDescription;
  icon?: ConfluenceSpaceIcon;
  homepage?: ConfluencePage;
  operations?: ConfluenceOperationCheckResult[];
  permissions?: ConfluenceSpacePermission[];
  settings?: ConfluenceSpaceSettings;
  theme?: ConfluenceSpaceTheme;
  lookAndFeel?: ConfluenceSpaceLookAndFeel;
  history?: ConfluenceSpaceHistory;
}

export interface ConfluenceGenericLinks {
  base?: string;
  self?: string;
  tinyui?: string;
  editui?: string;
  webui?: string;
  context?: string;
  collection?: string;
}

export interface ApiResource {
  expandable?: JsonObject;
  links?: ConfluenceGenericLinks;
}

export interface ConfluenceUserIcon {
}

export interface ConfluenceUserDetails {
}

export interface ConfluenceUser {
  type?: ConfluenceUserType;
  accountType?: ConfluenceUserAccountType;
  details?: ConfluenceUserDetails;
  isExternalCollaborator?: boolean;
  externalCollaborator?: boolean;
  username?: string;
  userKey?: string;
  accountId?: string;
  email?: string;
  publicName?: string;
  displayName?: string;
  timeZone?: string;
  profilePicture?: ConfluenceUserIcon;
  operations?: ConfluenceOperationCheckResult[];
  personalSpace?: ConfluenceSpace;
}

export interface ConfluenceUsersUserKeys {
  users?: ConfluenceUser[];
  userKeys?: string[];
}


export interface ConfluenceGroup {
  type?: ConfluenceGroupType;
  name?: string;
  id?: string;
}

export interface ConfluencePageVersion {
  by?: ConfluenceUser;
  when: string;
  authorId?: string;
  createdAt?: string;
  friendlyWhen?: string;
  message?: string;
  number: number;
  minorEdit: boolean;
  // eslint-disable-next-line no-use-before-define
  content?: ConfluencePage;
  collaborators?: ConfluenceUsersUserKeys;
  contentTypeModified?: boolean;
  confRev?: string;
  syncRev?: string;
  syncRevSource?: string;

}

export interface ConfluencePageContributors {
  publishers?: ConfluenceUsersUserKeys;
}

export interface ConfluencePageHistory {
  latest?: boolean;
  contributors?: ConfluencePageContributors;
  createdDate?: string;
  createdBy?: ConfluenceUser;
  ownedBy?: ConfluenceUser;
  lastUpdated?: ConfluencePageVersion;
  previousVersion?: ConfluencePageVersion;
  nextVersion?: ConfluencePageVersion;
}

export interface ConfluenceMediaToken {
  collectionIds?: string[];
  contentId?: string;
  expiryDateTime?: string;
  fileIds?: string[];
  token?: string;
}
export interface ConfluenceWebResourceDependencies {
}

export interface ConfluenceEmbeddable {
}

export interface ConfluenceEmbeddedContent {
  entityId?: number
  entityType?: string;
  entity?: ConfluenceEmbeddable
}

export interface ConfluenceContentBody {
  value?: string;
  representation?: ConfluenceContentBodyRepresentation;
  embeddedContent?: ConfluenceEmbeddedContent[];
  mediaToken?: ConfluenceMediaToken;
  webresource?: ConfluenceWebResourceDependencies;
}

export interface ConfluencePageBodyWrite {
  representation?: ConfluenceContentBodyRepresentation;
  value?: string;
}

// TODO: Add the rest of the representations.
// Confluence API returns body as a map of represenation -> value
// This interface represents that mapping.
export interface ConfluencePageBody {
  storage?: ConfluenceContentBody;
}

export interface ConfluenceContentChildren {
  page?: PaginatedResults<ConfluencePage>;
}

// This is the same as "Content"
export interface ConfluencePage {
  id: string | number;
  status: string;
  title: string;
  type?: string;
  authorId?: string;
  parentId?: string | number;
  spaceId?: string | number;
  createdAt?: string;
  macroRenderedOutput?: JsonObject;
  extensions?: JsonObject;
  ancestors?: JsonObject[];
  container?: JsonObject;
  body?: ConfluencePageBody;
  space?: ConfluenceSpace;
  history?: ConfluencePageHistory;
  version?: ConfluencePageVersion;
  children?: ConfluenceContentChildren;
  _links?: ConfluenceGenericLinks;
}

export interface UpdateConfluenceContentInput {
  id: string;
  body: string;
}

// This is made up, not part of any official Atlassian documentation
export interface ConfluenceSearchResultWithBody {
  id: string | number;
  type: ConfluenceContentType;
  status: ConfluenceContentStatus;
  title: string;
  body: {
    storage: ConfluenceContentBody;
  },
  _links?: ConfluenceGenericLinks;
}

export interface ContainerSummary {
  title: string;
  displayUrl: string;
}

export interface Breadcrumb {
  label: string;
  url: string;
  separator: string;
}

// I don't know what this is, it's documented here but the actual response is completely different.
// https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-search/#api-wiki-rest-api-search-get
// export interface ConfluenceSearchResult {
//   content?: ConfluencePage;
//   user?: ConfluenceUser;
//   space?: ConfluenceSpace;
//   title: string;
//   excerpt?: string;
//   url?: string;
//   resultParentContainer?: ContainerSummary;
//   resultGlobalContainer?: ContainerSummary;
//   breadcrumbs?: Breadcrumb[];
//   entityType?: string;
//   iconCssClass?: string;
//   lastModified?: string;
//   friendlyLastModified?: string;
//   score?: number;
// }

export interface SystemInfoEntity {
  cloudId: string;
  commitHash: string;
  baseUrl?: string;
  edition?: string;
  siteTitle?: string;
  defaultLocale?: string;
  defaultTimeZone?: string;
}
