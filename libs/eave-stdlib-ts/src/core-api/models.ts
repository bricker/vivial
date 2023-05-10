import * as enums from './enums.js';

export type AccessRequest = {
  id: string;
  visitor_id?: string;
  email: string;
  created: Date;
}

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