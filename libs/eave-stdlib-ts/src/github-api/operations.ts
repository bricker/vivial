import { Subscription } from '../core-api/models.js';

export type GetGithubUrlContentRequestBody = {
  eave_team_id: string;
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export type CreateGithubResourceSubscriptionRequestBody = {
  eave_team_id: string;
  url: string;
}

export type CreateGithubResourceSubscriptionResponseBody = {
  subscription: Subscription | null;
}
