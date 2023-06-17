import { sharedConfig } from '../../config.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { SlackInstallation, SlackInstallationInput } from '../models/slack.js';
import { Team } from '../models/team.js';

export type GetSlackInstallationRequestBody = {
  slack_integration: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: Team;
  slack_integration: SlackInstallation;
}

export async function getSlackInstallation(args: RequestArgsOrigin & {input: GetSlackInstallationRequestBody}): Promise<GetSlackInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/slack/query`,
    ...args,
  });
  const responseData = <GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}
