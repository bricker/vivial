import { Subscription } from "../core-api/models/subscriptions.js";

export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}

export type CreateGithubResourceSubscriptionResponseBody = {
  subscription: Subscription | null;
}
