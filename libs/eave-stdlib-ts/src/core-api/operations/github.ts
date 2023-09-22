import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, makeRequest } from '../../requests.js';
import { GithubInstallation, GithubInstallationInput } from '../models/github.js';
import { Team } from '../models/team.js';
import { CoreApiEndpointConfiguration } from './shared.js';

export type GetGithubInstallationRequestBody = {
  github_integration: GithubInstallationInput;
}

export type GetGithubInstallationResponseBody = {
  team: Team;
  github_integration: GithubInstallation;
}

export class GetGithubInstallationOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/integrations/github/query" })

  static async perform(args: RequestArgsOrigin & {input: GetGithubInstallationRequestBody}): Promise<GetGithubInstallationResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetGithubInstallationResponseBody>(await resp.json());
    return responseData;
  }
}