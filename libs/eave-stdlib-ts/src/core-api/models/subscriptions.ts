export enum SubscriptionSourcePlatform {
  slack = 'slack',
  github = 'github',
  jira = 'jira',
}

export enum SubscriptionSourceEvent {
  slack_message = 'slack_message',
  github_file_change = 'github_file_change',
  jira_issue_comment = 'jira_issue_comment',
}

export type SubscriptionSource = {
  platform: SubscriptionSourcePlatform;
  event: SubscriptionSourceEvent;
  id: string;
}

export type SubscriptionInput = {
  source: SubscriptionSource;
}

export type Subscription = {
  id: string;
  document_reference_id: string | null;
  source: SubscriptionSource;
}

export type DocumentReferenceInput = {
  id: string;
}

export type DocumentReference = {
  id: string;
  document_id: string;
  document_url: string;
}
