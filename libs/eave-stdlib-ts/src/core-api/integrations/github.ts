import { sharedConfig } from '../../config.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { Team } from '../team.js';

export type GithubInstallationInput = {
  github_install_id: string;
}

export type GithubInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  github_install_id: string;
}

export type GetGithubInstallationRequestBody = {
  github_integration: GithubInstallationInput;
}

export type GetGithubInstallationResponseBody = {
  team: Team;
  github_integration: GithubInstallation;
}

export async function getGithubInstallation({ origin, input }: RequestArgsOrigin & {input: GetGithubInstallationRequestBody}): Promise<GetGithubInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/github/query`,
    origin,
    input,
  });
  const responseData = <GetGithubInstallationResponseBody>(await resp.json());
  return responseData;
}
