import { sharedConfig } from "../config.js";
import { CreateSubscriptionResponseBody } from "../core-api/operations/subscriptions.js";
import { EaveApp } from "../eave-origins.js";
import { CtxArg, RequestArgsAccountId, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from "../requests.js";
import { GithubRepoInput } from "./models.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_github_app);

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}

export async function createSubscription(args: RequestArgsOrigin & RequestArgsTeamId & CtxArg & {
  input: CreateGithubResourceSubscriptionRequestBody,
}): Promise<CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github/api/subscribe`,
    ...args,
  });
  const responseData = <CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}

export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export async function getFileContent(args: RequestArgsOrigin & RequestArgsTeamId & CtxArg & {
  input: GetGithubUrlContentRequestBody,
}): Promise<GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github/api/content`,
    ...args,
  });
  const responseData = <GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}

export type RunApiDocumentationTaskRequestBody = {
  repo: GithubRepoInput;
}

export async function runApiDocumentationTask(args: RequestArgsOrigin & RequestArgsTeamId & CtxArg & {
  input: RunApiDocumentationTaskRequestBody,
}): Promise<void> {
  await makeRequest({
    url: `${baseUrl}/_/github/run-api-documentation`,
    ...args,
  });
}
