import { Team } from '../models/team.js';
import { ConnectInstallation, QueryConnectInstallationInput, RegisterConnectInstallationInput } from '../models/connect.js';
import { CtxArg, RequestArgsOrigin, makeRequest } from '../../requests.js';
import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CORE_API_BASE_URL } from './shared.js';

export type RegisterConnectInstallationRequestBody = {
  connect_integration: RegisterConnectInstallationInput;
}
export type RegisterConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
}

export async function registerConnectInstallation(args: RequestArgsOrigin & {input: RegisterConnectInstallationRequestBody}): Promise<RegisterConnectInstallationResponseBody> {
  const resp = await makeRequest({
    url: `${CORE_API_BASE_URL}/integrations/connect/register`,
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
    url: `${CORE_API_BASE_URL}/integrations/connect/query`,
    ...args,
  });
  const responseData = <QueryConnectInstallationResponseBody>(await resp.json());
  return responseData;
}
