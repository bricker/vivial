// Copied from https://developer.atlassian.com/platform/forge/events-reference/jira/
// As of this writing, Atlassian does not publicly provide these type definitions.

// Objects
interface ApiResource {
  self: string;
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

export interface JiraProject extends ApiResource {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
  simplified: boolean;
  avatarUrls: {[key: string]: string };
}

export interface JiraIssueType extends ApiResource {
  id: string;
  description: string;
  iconUrl: string;
  name: string;
  subtask: boolean;
  avatarId: number;
}

export interface JiraStatusCategory extends ApiResource {
  id: number;
  key: string;
  colorName: string;
  name: string;
}

export interface JiraStatus extends ApiResource {
  description: string;
  iconUrl: string;
  name: string;
  id: string;
  statusCategory: JiraStatusCategory;
}

export interface JiraUser extends ApiResource {
  accountId: string;
  avatarUrls?: any;
  displayName?: string;
  active?: boolean;
  timeZone?: string;
  accountType?: string;
}

export interface JiraIssue extends ApiResource {
  id: string;
  key: string;
  fields: {
    summary?: string;
    issueType?: JiraIssueType;
    creator?: JiraUser;
    created?: string;
    project?: JiraProject;
    reporter?: JiraUser;
    assignee?: JiraUser | null;
    updated?: string;
    status?: JiraStatus;
  };
}

export interface JiraAssociatedUsers {
  associatedUsers: JiraUser[];
}

export interface JiraIssueLinkType {
  id: string;
  name: string;
  inward: string;
  outward: string;
}

export interface JiraChange {
  field: string;
  fieldId: string;
  from: string | null;
  fromString: string | null;
  to: string | null;
  toString: string | null;
}

export interface JiraChangelog {
  items: JiraChange[];
}

export interface JiraComment extends ApiResource {
  id: string;
  author: JiraUser;
  body: string;
  updateAuthor: JiraUser;
  created: string;
  updated: string;
  jsdPublic: boolean;
}

export interface IdKey {
  id: string;
  key: string;
}

export interface JiraStatusId {
  id: string;
}

export interface JiraTransition {
  id: string;
  name: string;
  from: JiraStatusId;
  to: JiraStatusId;
}

export interface JiraContext {
  issue: IdKey;
  project: IdKey;
  user: JiraUser;
  transition: JiraTransition;
}

// Incoming Event Payloads
// The names of these payloads are based on the event name
// Example: "avi:jira:commented:issue" -> CommentedIssueEventPayload"
// Forge only:
// export interface EventPayload {
//   eventType: string;
//   environment?: { id: string };
//   contextToken?: string;
//   context?: {
//     cloudId?: string;
//     moduleKey?: string;
//   };
//   selfGenerated?: boolean;
//   retryContext?: {
//     retryData?: unknown;
//     retryCount?: number;
//     retryReason?: string;
//   };
// }

export interface WebhookEvent {
  timestamp: number;
  webhookEvent: string; // Name of the event
  eventType: string;
}

export interface CommentCreatedEventPayload extends WebhookEvent {
  issue?: JiraIssue;
  comment: JiraComment;
}
