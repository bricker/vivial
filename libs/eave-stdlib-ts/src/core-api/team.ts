import { sharedConfig } from '../config.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../lib/requests.js';
import { Integrations } from './integrations/map.js';

export enum DocumentPlatform {
  eave = 'eave',
  confluence = 'confluence',
  google_drive = 'google_drive',
}

export type Team = {
  id: string;
  name: string;
  document_platform?: DocumentPlatform;
}

export type TeamInput = {
  id: string;
}

export type GetTeamResponseBody = {
  team: Team;
  integrations: Integrations;
}

export async function getTeam({ origin, teamId }: RequestArgsOriginAndTeamId): Promise<GetTeamResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/team/query`,
    origin,
    teamId,
  });
  const responseData = <GetTeamResponseBody>(await resp.json());
  return responseData;
}
