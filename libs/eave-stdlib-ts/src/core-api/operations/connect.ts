import { Team } from '../models/team.js';
import { ConnectInstallation, QueryConnectInstallationInput, RegisterConnectInstallationInput } from '../models/connect.js';
import { RequestArgsOrigin, makeRequest } from '../../lib/requests.js';
import { sharedConfig } from '../../config.js';

export type RegisterConnectInstallationRequestBody = {
  connect_integration: RegisterConnectInstallationInput;
}
export type RegisterConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
}

export async function registerConnectInstallation({ origin, input }: RequestArgsOrigin & {input: RegisterConnectInstallationRequestBody}): Promise<RegisterConnectInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/connect/register`,
    input,
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

export async function queryConnectInstallation({ origin, input }: RequestArgsOrigin & {input: QueryConnectInstallationRequestBody}): Promise<QueryConnectInstallationResponseBody> {
  const resp = await makeRequest({
    origin,
    url: `${sharedConfig.eaveApiBase}/integrations/connect/query`,
    input,
  });
  const responseData = <QueryConnectInstallationResponseBody>(await resp.json());
  return responseData;
}