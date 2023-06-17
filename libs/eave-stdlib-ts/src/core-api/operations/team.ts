import { sharedConfig } from '../../config.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../../lib/requests.js';
import { Integrations } from '../models/integrations.js';
import { Team } from '../models/team.js';

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export async function getTeam(args: RequestArgsOriginAndTeamId): Promise<GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/team/query`,
    ...args,
  });
  const responseData = <GetTeamResponseBody>(await resp.json());
  return responseData;
}
