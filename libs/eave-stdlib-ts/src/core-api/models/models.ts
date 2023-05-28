import * as enums from '../enums';

export type DocumentReference = {
  id: string;
  document_id: string;
  document_url: string;
}

export type SubscriptionSource = {
  platform: enums.SubscriptionSourcePlatform;
  event: enums.SubscriptionSourceEvent;
  id: string;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent?: EaveDocument;
}

export type Subscription = {
  id: string;
  document_reference_id?: string;
  source: SubscriptionSource;
}

export type Team = {
  id: string;
  name: string;
  document_platform?: enums.DocumentPlatform;
}

export type SlackInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  slack_team_id: string;
  bot_token: string;
  bot_id: string;
  bot_user_id?: string;
}

export type GithubInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  github_install_id: string;
}

export type ConfluenceSpace = {
  key: string;
  name: string;
}

export type AtlassianInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  atlassian_cloud_id: string;
  confluence_space?: string;
  available_confluence_spaces?: Array<ConfluenceSpace>;
  oauth_token_encoded: string;
}

/**
 * Key-value mapping of Integration to Installation info.
 * The keys here will match the enum cases in enums.Integration
 */
export type Integrations = {
  github?: GithubInstallation;
  slack?: SlackInstallation;
  atlassian?: AtlassianInstallation;
}
