import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export type RunApiDocumentationTaskRequestBody = {
  repo: GithubRepoInput;
}

export class RunApiDocumentationTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/_/github/run-api-documentation",
    authRequired: false,
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
