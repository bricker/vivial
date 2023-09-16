import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, makeRequest } from '../../requests.js';
import { GithubInstallation, GithubInstallationInput } from '../models/github.js';
import { Team } from '../models/team.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type GetGithubInstallationRequestBody = {
  github_integration: GithubInstallationInput;
}

export type GetGithubInstallationResponseBody = {
  team: Team;
  github_integration: GithubInstallation;
}

export async function getGithubInstallation(args: RequestArgsOrigin & {input: GetGithubInstallationRequestBody}): Promise<GetGithubInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/integrations/github/query`,
    ...args,
  });
  const responseData = <GetGithubInstallationResponseBody>(await resp.json());
  return responseData;
}
