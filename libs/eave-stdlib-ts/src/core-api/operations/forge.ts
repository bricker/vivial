import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { sharedConfig } from '../../config.js';
import { ForgeInstallation, QueryForgeInstallationInput, RegisterForgeInstallationInput, UpdateForgeInstallationInput } from '../models/forge.js';
import { Team } from '../models/team.js';


export type QueryForgeInstallationRequestBody = {
  forge_integration: QueryForgeInstallationInput;
}

export type QueryForgeInstallationResponseBody = {
  team: Team;
  forge_integration: ForgeInstallation;
}
export type RegisterForgeInstallationRequestBody = {
  forge_integration: RegisterForgeInstallationInput;
}
export type RegisterForgeInstallationResponseBody = {
  forge_integration: ForgeInstallation;
}

export type UpdateForgeInstallationRequestBody = {
  forge_integration: UpdateForgeInstallationInput;
}
export type UpdateForgeInstallationResponseBody = {
  team: Team;
  forge_integration: ForgeInstallation;
}

export async function queryForgeInstallation({ origin, input }: RequestArgsOrigin & {input: QueryForgeInstallationInput}): Promise<QueryForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/forge/query`,
    input,
  });
  const responseData = <QueryForgeInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function registerForgeInstallationInsecure({ origin, sharedSecret, input }: RequestArgsOrigin & {sharedSecret: string, input: RegisterForgeInstallationRequestBody}): Promise<RegisterForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    accessToken: sharedSecret,
    sign: false, // TODO: Get signing working
    url: `${sharedConfig.eaveApiBase}/integrations/forge/register`,
    input,
  });
  const responseData = <RegisterForgeInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function updateForgeInstallationInsecure({ origin, sharedSecret, input }: RequestArgsOrigin & {sharedSecret: string, input: UpdateForgeInstallationRequestBody}): Promise<UpdateForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    accessToken: sharedSecret,
    sign: false,
    url: `${sharedConfig.eaveApiBase}/integrations/forge/update`,
    input,
  });
  const responseData = <UpdateForgeInstallationResponseBody>(await resp.json());
  return responseData;
}
