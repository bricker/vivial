// As of this writing, Atlassian does not publicly provide these type definitions.

// Objects
interface ApiResource {
  self: string;
}

export interface JiraProject extends ApiResource {
  id: string;
  key: string;
  name: string;
  projectTypeKey: string;
  simplified: boolean;
  avatarUrls: { [key: string]: string };
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

export interface JiraIdKey {
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
  issue: JiraIdKey;
  project: JiraIdKey;
  user: JiraUser;
  transition: JiraTransition;
}

// Incoming Event Payloads
// The names of these payloads are based on the event name
// Example: "avi:jira:commented:issue" -> CommentedIssueEventPayload"
// Forge only:
// export interface JiraEventPayload {
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

export interface JiraWebhookEvent {
  timestamp: number;
  webhookEvent: string; // Name of the event, eg 'comment_created'. https://developer.atlassian.com/cloud/jira/platform/modules/webhook/
  eventType: string; // 'primaryAction', for example (I'm not sure how many others there are)
}

export interface JiraCommentCreatedEventPayload extends JiraWebhookEvent {
  issue?: JiraIssue;
  comment: JiraComment;
}
