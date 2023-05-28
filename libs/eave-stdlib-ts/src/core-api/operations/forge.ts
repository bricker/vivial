import * as forgemodels from '../models/forge';
import * as models from '../models/models';
import { makeRequest } from '../../lib/requests';
import { sharedConfig } from '../../config';
import { EaveOrigin } from '../../eave-origins';

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
  webtrigger_url: string;
  confluence_space_key?: string;
}

export type QueryForgeInstallationRequestBody = {
  forge_integration: QueryForgeInstallationInput;
}

export type QueryForgeInstallationResponseBody = {
  team: models.Team;
  forge_integration: forgemodels.ForgeInstallation;
}
export type RegisterForgeInstallationRequestBody = {
  forge_integration: RegisterForgeInstallationInput;
}
export type RegisterForgeInstallationResponseBody = {
  team: models.Team;
  forge_integration: forgemodels.ForgeInstallation;
}

export type UpdateForgeInstallationRequestBody = {
  forge_integration: UpdateForgeInstallationInput;
}
export type UpdateForgeInstallationResponseBody = {
  team: models.Team;
  forge_integration: forgemodels.ForgeInstallation;
}

export async function queryForgeInstallation(origin: EaveOrigin | string, input: QueryForgeInstallationRequestBody): Promise<QueryForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/forge/query`,
    input,
  });
  const responseData = <QueryForgeInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function registerForgeInstallation(origin: EaveOrigin | string, input: RegisterForgeInstallationRequestBody): Promise<RegisterForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/forge/register`,
    input,
  });
  const responseData = <RegisterForgeInstallationResponseBody>(await resp.json());
  return responseData;
}

export async function updateForgeInstallation(origin: EaveOrigin | string, input: UpdateForgeInstallationRequestBody): Promise<UpdateForgeInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/forge/update`,
    input,
  });
  const responseData = <UpdateForgeInstallationResponseBody>(await resp.json());
  return responseData;
}
