export declare type JsonScalar =
  string |
  number |
  null

export declare type JsonObject = {[key: string]: JsonScalar | JsonScalar[] | JsonObject | JsonObject[] };

// export declare type JsonValue =
//   JsonScalar |
//   JsonScalar[] |
//   JsonObject |
//   JsonObject[];

// Copied from https://developer.atlassian.com/platform/forge/events-reference/jira/
// As of this writing, Atlassian does not publicly provide these type definitions.

// Objects
interface ApiResource {
  self: string;
}

export interface App {
  id: string;
  version: string;
}

// This enum definition is incomplete
// https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
export enum ContentType {
  doc = 'doc',
  paragraph = 'paragraph',
  text = 'text',
  mention = 'mention',
  link = 'link',
}

// LinkAttrs: https://developer.atlassian.com/cloud/jira/platform/apis/document/marks/link/#attributes

// This object definition is incomplete
// https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
export interface Content {
  type: string;
  text?: string;
  content?: Content[];
  marks?: Content[];
  attrs?: unknown;
}

export interface Project extends ApiResource {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
  simplified: boolean;
  avatarUrls: {[key: string]: string };
}

export interface IssueType extends ApiResource {
  id: string;
  description: string;
  iconUrl: string;
  name: string;
  subtask: boolean;
  avatarId: number;
}

export interface StatusCategory extends ApiResource {
  id: number;
  key: string;
  colorName: string;
  name: string;
}

export interface Status extends ApiResource {
  description: string;
  iconUrl: string;
  name: string;
  id: string;
  statusCategory: StatusCategory;
}

export interface User {
  accountId: string;
}

export interface Issue {
  id: string;
  key: string;
  fields: {
    summary?: string;
    issueType?: IssueType;
    creator?: User;
    created?: string;
    project?: Project;
    reporter?: User;
    assignee?: User | null;
    updated?: string;
    status?: Status;
  };
}

export interface AssociatedUsers {
  associatedUsers: User[];
}

export interface IssueLinkType {
  id: string;
  name: string;
  inward: string;
  outward: string;
}

export interface Change {
  field: string;
  fieldId: string;
  from: string | null;
  fromString: string | null;
  to: string | null;
  toString: string | null;
}

export interface Changelog {
  items: Change[];
}

export interface Comment {
  id: string;
  author: User;
  body: unknown;
  updateAuthor: User;
  created: string;
  updated: string;
  jsdPublic: boolean;
}

export interface IdKey {
  id: string;
  key: string;
}

export interface StatusId {
  id: string;
}

export interface Transition {
  id: string;
  name: string;
  from: StatusId;
  to: StatusId;
}

export interface Context {
  issue: IdKey;
  project: IdKey;
  user: User;
  transition: Transition;
}

// Incoming Event Payloads
// The names of these payloads are based on the event name
// Example: "avi:jira:commented:issue" -> CommentedIssueEventPayload"
export interface EventPayload {
  eventType: string;
}

export interface CommentedIssueEventPayload extends EventPayload {
  issue: Issue;
  atlassianId: string;
  associatedUsers: AssociatedUsers;
  comment: Comment;
}

export interface MentionedCommentEventPayload extends EventPayload {
  issue: Issue;
  atlassianId: string;
  mentionedAccountIds: string[];
  comment: Comment;
}

// https://developer.atlassian.com/platform/forge/events-reference/life-cycle/#installation
export interface InstalledAppEventPayload {
  id: string;
  installerAccountId: string;
  app: App;
}

// https://developer.atlassian.com/platform/forge/events-reference/life-cycle/#upgrade
export interface UpgradedAppEventPayload {
  id: string;
  installerAccountId: string;
  app: App;
}

export interface WebTriggerRequestPayload {
  // https://developer.atlassian.com/platform/forge/events-reference/web-trigger/#request
  body?: string;
  headers?: {[key: string]: string[]};
  call?: { functionKey?: string };
  method: string;
  path: string;
  queryParameters?: {[key: string]: string[]};
  context?: {
    cloudId?: string;
    moduleKey?: string;
  };
  contextToken?: string;
}

export interface WebTriggerResponsePayload {
  // https://developer.atlassian.com/platform/forge/events-reference/web-trigger/#response
  body?: string;
  headers?: {[key: string]: string[]};
  statusCode: number;
  statusText?: string;
}
