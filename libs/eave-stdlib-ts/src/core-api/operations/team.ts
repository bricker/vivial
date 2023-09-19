import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { Integrations } from '../models/integrations.js';
import { Team } from '../models/team.js';
import { CoreApiEndpointConfiguration } from './shared.js';

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export class GetTeamOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/team/query" })

  static async perform(args: RequestArgsTeamId): Promise<GetTeamResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <GetTeamResponseBody>(await resp.json());
    return responseData;
  }
}