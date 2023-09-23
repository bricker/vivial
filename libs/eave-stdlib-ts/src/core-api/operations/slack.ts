import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, makeRequest } from '../../requests.js';
import { SlackInstallation, SlackInstallationInput } from '../models/slack.js';
import { Team } from '../models/team.js';
import { CoreApiEndpointConfiguration } from './shared.js';

export type GetSlackInstallationRequestBody = {
  slack_integration: SlackInstallationInput;
}

export type GetSlackInstallationResponseBody = {
  team: Team;
  slack_integration: SlackInstallation;
}

export class GetSlackInstallationOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/integrations/slack/query" })

  static async perform(args: RequestArgsOrigin & {input: GetSlackInstallationRequestBody}): Promise<GetSlackInstallationResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetSlackInstallationResponseBody>(await resp.json());
    return responseData;
  }
}