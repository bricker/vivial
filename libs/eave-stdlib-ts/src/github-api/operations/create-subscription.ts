import { sharedConfig } from "../../config.js";
import { CreateSubscriptionResponseBody } from "../../core-api/operations/subscriptions.js";
import { EaveApp } from "../../eave-origins.js";
import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export const config = new GithubAppEndpointConfiguration({
  path: "/github/api/subscribe",
  authRequired: false,
})

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}

export async function createGithubResourceSubscription(args: RequestArgsTeamId & {
  input: CreateGithubResourceSubscriptionRequestBody,
}): Promise<CreateSubscriptionResponseBody> {
  const resp = await makeRequest({
    url: config.url,
    ...args,
  });

  const responseData = <CreateSubscriptionResponseBody>(await resp.json());
  return responseData;
}
