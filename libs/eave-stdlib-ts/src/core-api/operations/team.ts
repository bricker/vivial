import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { Integrations } from '../models/integrations.js';
import { Team } from '../models/team.js';
import { CORE_API_BASE_URL } from './shared.js';

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export async function getTeam(args: RequestArgsTeamId): Promise<GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${CORE_API_BASE_URL}/team/query`,
    ...args,
  });
  const responseData = <GetTeamResponseBody>(await resp.json());
  return responseData;
}
