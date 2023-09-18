import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, makeRequest } from '../../requests.js';
import { SlackInstallation, SlackInstallationInput } from '../models/slack.js';
import { Team } from '../models/team.js';
import { CORE_API_BASE_URL } from './shared.js';

export type GetSlackInstallationRequestBody = {
  slack_integration: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: Team;
  slack_integration: SlackInstallation;
}

export async function getSlackInstallation(args: RequestArgsOrigin & {input: GetSlackInstallationRequestBody}): Promise<GetSlackInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${CORE_API_BASE_URL}/integrations/slack/query`,
    ...args,
  });
  const responseData = <GetSlackInstallationResponseBody>(await resp.json());
  return responseData;
}
