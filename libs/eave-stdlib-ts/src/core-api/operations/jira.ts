import { Team } from '../models/team.js';
import { JiraInstallation, RegisterJiraInstallationInput } from '../models/jira.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { sharedConfig } from '../../config.js';

export type RegisterJiraInstallationRequestBody = {
  jira_integration: RegisterJiraInstallationInput;
}
export type RegisterJiraInstallationResponseBody = {
  team?: Team;
  jira_integration: JiraInstallation;
}

export async function registerJiraInstallationInsecure({ origin, input }: RequestArgsOrigin & {input: RegisterJiraInstallationRequestBody}): Promise<RegisterJiraInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/jira/register`,
    input,
  });
  const responseData = <RegisterJiraInstallationResponseBody>(await resp.json());
  return responseData;
}
