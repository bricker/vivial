import { sharedConfig } from '../../config.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { SlackInstallation, SlackInstallationInput } from '../models/slack.js';
import { Team } from '../models/team.js';

export type GetSlackInstallationRequestBody = {
  slack_installation: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: Team;
  slack_installation: SlackInstallation;
}

export async function getSlackInstallation({ origin, input }: RequestArgsOrigin & {input: GetSlackInstallationRequestBody}): Promise<GetSlackInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/slack/query`,
    origin,
    input,
  });
  const responseData = <GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}
