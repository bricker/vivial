import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { Integrations } from '../models/integrations.js';
import { Team } from '../models/team.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export async function getTeam(args: RequestArgsTeamId): Promise<GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/team/query`,
    ...args,
  });
  const responseData = <GetTeamResponseBody>(await resp.json());
  return responseData;
}
