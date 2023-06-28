import { sharedConfig } from '../../config.js';
import { EaveService } from '../../eave-origins.js';
import { RequestArgsOrigin, appengineBaseUrl, makeRequest } from '../../requests.js';
import { GithubInstallation, GithubInstallationInput } from '../models/github.js';
import { Team } from '../models/team.js';

const baseUrl = appengineBaseUrl(EaveService.api);

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
