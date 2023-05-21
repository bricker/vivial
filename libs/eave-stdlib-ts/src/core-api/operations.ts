import * as models from './models.js';

export type DocumentInput = {
  title: string;
  content: string;
  parent?: DocumentInput;
}

export type DocumentReferenceInput = {
  id: string;
}

export type SubscriptionInput = {
  source: models.SubscriptionSource;
}

export type TeamInput = {
  id: string;
}

export type SlackInstallationInput = {
  slack_team_id: string;
}

export type GithubInstallationInput = {
  github_install_id: string;
}

export type UpsertDocumentRequestBody = {
  document: DocumentInput;
  subscriptions: Array<models.Subscription>;
}
export type UpsertDocumentResponseBody = {
  team: models.Team;
  subscriptions: Array<models.Subscription>;
  document_reference: models.DocumentReference;
}

export type StatusResponseBody = {
  service: string;
  version: string;
  status: string;
}

export type CreateAccessRequestRequestBody = {
  visitor_id?: string;
  email: string;
  opaque_input?: unknown;
}

export type GetSubscriptionRequestBody = {
  subscription: SubscriptionInput;
}

export type GetSubscriptionResponseBody = {
  team: models.Team;
  subscription: models.Subscription;
  document_reference?: models.DocumentReference;
}

export type CreateSubscriptionRequestBody = {
  subscription: SubscriptionInput;
  document_reference?: DocumentReferenceInput;
}

export type CreateSubscriptionResponseBody = {
  team: models.Team;
  subscription: models.Subscription;
  document_reference?: models.DocumentReference;
}

export type GetSlackInstallationRequestBody = {
  slack_installation: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: models.Team;
  slack_installation: models.SlackInstallation;
}

export type GetGithubInstallationRequestBody = {
  github_installation: GithubInstallationInput;
}

export type GetGithubInstallationResponseBody = {
  team: models.Team;
  github_installation: models.GithubInstallation;
}

export type DeleteSubscriptionRequestBody = {
  subscription: SubscriptionInput;
}

export type GetTeamResponseBody = {
  team: models.Team;
  integrations: models.Integrations;
}
