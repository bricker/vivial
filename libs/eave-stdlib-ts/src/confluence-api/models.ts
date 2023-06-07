import { JsonObject } from '../types.js';

export interface ConfluenceSearchParamsInput {
  space_key?: string;
  text: string;
}

export interface DeleteContentInput {
  content_id: string;
}

export enum ConfluenceSpaceType {
  global = 'global',
  personal = 'personal',
}

export enum ConfluenceSpaceStatus {
  current = 'current',
  archived = 'archived',
}

export interface BodyType {
  representation: string;
  value: string;
}

export interface ConfluenceSpaceDescription {
  plain: BodyType;
  view: BodyType;
}

export interface ConfluenceSpace {
  id: string | number; // https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-905
  key: string;
  name: string;
  type: ConfluenceSpaceType;
  status: ConfluenceSpaceStatus;
  homepageId: string | number; // https://developer.atlassian.com/cloud/confluence/changelog/#CHANGE-905
  description: ConfluenceSpaceDescription;
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

export interface ConfluenceOperationCheckResult {
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
  _links?: ConfluenceGenericLinks;
}

// This is made up, not part of any official Atlassian documentation
export interface ConfluenceSearchResultWithBody {
  id: string | number;
  type: ConfluenceContentType;
  status: ConfluenceContentStatus;
  title: string;
  body: {
    storage: ConfluenceContentBody;
  }
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
