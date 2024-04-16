import {
  RequestArgsOrigin,
  RequestArgsTeamId,
  makeRequest,
} from "../../requests.js";
import {
  GithubInstallation,
  GithubInstallationQueryInput,
} from "../models/github-installation.js";
import { Team, TeamQueryInput } from "../models/team.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type QueryGithubInstallationRequestBody = {
  github_installation?: GithubInstallationQueryInput;
  team?: TeamQueryInput;
};

export type QueryGithubInstallationResponseBody = {
  team: Team | null;
  github_installation: GithubInstallation;
};

export class QueryGithubInstallationOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/_/github_installations/query",
    signatureRequired: false,
    authRequired: false,
    teamIdRequired: false,
  });

  static async perform(
    args: RequestArgsOrigin & { input: QueryGithubInstallationRequestBody },
  ): Promise<QueryGithubInstallationResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <QueryGithubInstallationResponseBody>await resp.json();
    return responseData;
  }
}

export type DeleteGithubInstallationRequestBody = {
  github_installation: GithubInstallationQueryInput;
};

export class DeleteGithubInstallationOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/_/github_installations/delete",
    authRequired: false,
    signatureRequired: false,
  });

  static async perform(
    args: RequestArgsTeamId & { input: DeleteGithubInstallationRequestBody },
  ): Promise<void> {
    await makeRequest({
      config: this.config,
      ...args,
    });
  }
}
