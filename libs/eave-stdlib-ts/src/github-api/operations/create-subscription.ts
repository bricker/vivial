import { sharedConfig } from "../../config.js";
import { CreateSubscriptionResponseBody } from "../../core-api/operations/subscriptions.js";
import { EaveApp } from "../../eave-origins.js";
import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GITHUB_APP_API_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}

export class CreateGithubResourceSubscriptionOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_API_MOUNT_PATH,
    subPath: "/subscribe",
    authRequired: false,
  })

  static async perform(args: RequestArgsTeamId & {
    input: CreateGithubResourceSubscriptionRequestBody,
  }): Promise<CreateSubscriptionResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });

    const responseData = <CreateSubscriptionResponseBody>(await resp.json());
    return responseData;
  }
}