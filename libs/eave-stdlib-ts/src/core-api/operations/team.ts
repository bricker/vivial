import { EaveService } from '../../eave-origins.js';
import { RequestArgsOriginAndTeamId, appengineBaseUrl, makeRequest } from '../../requests.js';
import { Integrations } from '../models/integrations.js';
import { Team } from '../models/team.js';

const baseUrl = appengineBaseUrl(EaveService.api);

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export async function getTeam(args: RequestArgsOriginAndTeamId): Promise<GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/team/query`,
    ...args,
  });
  const responseData = <GetTeamResponseBody>(await resp.json());
  return responseData;
}
