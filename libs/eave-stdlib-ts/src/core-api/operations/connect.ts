import { Team } from '../models/team.js';
import { ConnectInstallation, QueryConnectInstallationInput, RegisterConnectInstallationInput } from '../models/connect.js';
import { RequestArgsOrigin, makeRequest } from '../../requests.js';
import { sharedConfig } from '../../config.js';

export type RegisterConnectInstallationRequestBody = {
  connect_integration: RegisterConnectInstallationInput;
}
export type RegisterConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
}

export async function registerConnectInstallation(args: RequestArgsOrigin & {input: RegisterConnectInstallationRequestBody}): Promise<RegisterConnectInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/connect/register`,
    ...args,
  });
  const responseData = <RegisterConnectInstallationResponseBody>(await resp.json());
  return responseData;
}

export type QueryConnectInstallationRequestBody = {
  connect_integration: QueryConnectInstallationInput;
}
export type QueryConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
}

export async function queryConnectInstallation(args: RequestArgsOrigin & {input: QueryConnectInstallationRequestBody}): Promise<QueryConnectInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/integrations/connect/query`,
    ...args,
  });
  const responseData = <QueryConnectInstallationResponseBody>(await resp.json());
  return responseData;
}
