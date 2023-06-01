import { Team } from '../models/team.js';
import { JiraInstallation, QueryJiraInstallationInput, RegisterJiraInstallationInput } from '../models/jira.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { sharedConfig } from '../../config.js';

export type RegisterJiraInstallationRequestBody = {
  jira_integration: RegisterJiraInstallationInput;
}
export type RegisterJiraInstallationResponseBody = {
  team?: Team;
  jira_integration: JiraInstallation;
}

export async function registerJiraInstallation({ origin, input }: RequestArgsOrigin & {input: RegisterJiraInstallationRequestBody}): Promise<RegisterJiraInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/jira/register`,
    input,
  });
  const responseData = <RegisterJiraInstallationResponseBody>(await resp.json());
  return responseData;
}

export type QueryJiraInstallationRequestBody = {
  jira_integration: QueryJiraInstallationInput;
}
export type QueryJiraInstallationResponseBody = {
  team?: Team;
  jira_integration: JiraInstallation;
}

export async function queryJiraInstallation({ origin, input }: RequestArgsOrigin & {input: QueryJiraInstallationRequestBody}): Promise<QueryJiraInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/jira/query`,
    input,
  });
  const responseData = <QueryJiraInstallationResponseBody>(await resp.json());
  return responseData;
}