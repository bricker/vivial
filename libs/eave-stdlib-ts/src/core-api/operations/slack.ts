import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { RequestArgsOrigin, makeRequest } from '../../requests.js';
import { SlackInstallation, SlackInstallationInput } from '../models/slack.js';
import { Team } from '../models/team.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type GetSlackInstallationRequestBody = {
  slack_integration: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: Team;
  slack_integration: SlackInstallation;
}

export async function getSlackInstallation(args: RequestArgsOrigin & {input: GetSlackInstallationRequestBody}): Promise<GetSlackInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/integrations/slack/query`,
    ...args,
  });
  const responseData = <GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}
