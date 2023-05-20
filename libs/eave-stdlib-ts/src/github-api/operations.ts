import { Subscription } from '../core-api/models';

export type GetGithubUrlContentRequestBody = {
  eaveTeamId: string;
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export type CreateGithubResourceSubscriptionRequestBody = {
  eaveTeamId: string;
  url: string;
}

export type CreateGithubResourceSubscriptionResponseBody = {
  subscription: Subscription | null;
}
