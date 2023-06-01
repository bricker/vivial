import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { sharedConfig } from '../../config.js';
import { Team } from '../team.js';

export enum EaveForgeInboundOperation {
  createDocument = 'createDocument',
  updateDocument = 'updateDocument',
  archiveDocument = 'archiveDocument',

}

export type ForgeInstallation = {
  id: string;
  forge_app_id: string;
  forge_app_version: string;
  forge_app_installation_id: string;
  forge_app_installer_account_id: string;
  webtrigger_url: string;
  confluence_space_key?: string;
}

export type QueryForgeInstallationInput = {
  forge_app_id: string;
  forge_app_installation_id: string;
}
export type RegisterForgeInstallationInput = {
  forge_app_id: string;
  forge_app_version: string;
  forge_app_installation_id: string;
  forge_app_installer_account_id: string;
  webtrigger_url: string;
  confluence_space_key?: string;
}

export type UpdateForgeInstallationInput = {
  forge_app_installation_id: string;
  forge_app_version?: string;
  forge_app_installer_account_id?: string;
  webtrigger_url?: string;
  confluence_space_key?: string;
}

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
