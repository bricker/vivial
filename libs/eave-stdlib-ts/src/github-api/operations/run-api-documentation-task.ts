import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GITHUB_APP_TASKS_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export type RunApiDocumentationTaskRequestBody = {
  repo: GithubRepoInput;
}

export class RunApiDocumentationTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_TASKS_MOUNT_PATH,
    subPath: "/run-api-documentation",
    authRequired: false,
    teamIdRequired: false,
    signatureRequired: false,
    originRequired: false,
  })

  static async perform(args: RequestArgsTeamId & {
    input: RunApiDocumentationTaskRequestBody,
  }): Promise<void> {
    await makeRequest({
      url: this.config.url,
      ...args,
    });
  }
}
