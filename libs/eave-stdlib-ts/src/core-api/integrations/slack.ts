import { sharedConfig } from '../../config.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { Team } from '../team.js';

export type SlackInstallationInput = {
  slack_team_id: string;
}

export type SlackInstallation = {
  id: string;
  /** eave TeamOrm model id */
  team_id: string;
  slack_team_id: string;
  bot_token: string;
  bot_id: string;
  bot_user_id?: string;
}

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
