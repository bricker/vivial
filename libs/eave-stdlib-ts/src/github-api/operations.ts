export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}
