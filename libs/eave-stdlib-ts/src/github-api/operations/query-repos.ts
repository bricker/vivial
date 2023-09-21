import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { ExternalGithubRepo } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export type QueryGithubReposResponseBody = {
  repos: ExternalGithubRepo[];
};

export class QueryGithubReposOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/github/api/repos/query",
    authRequired: false,
  });

  static async perform(
    args: RequestArgsTeamId,
  ): Promise<QueryGithubReposResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <QueryGithubReposResponseBody>await resp.json();
    return responseData;
  }
}
