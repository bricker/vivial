import { RequestArgsOrigin, makeRequest } from "../../requests.js";
import {
  ConnectInstallation,
  QueryConnectInstallationInput,
  RegisterConnectInstallationInput,
} from "../models/connect.js";
import { Team } from "../models/team.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type RegisterConnectInstallationRequestBody = {
  connect_integration: RegisterConnectInstallationInput;
};
export type RegisterConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
};

export class RegisterConnectInstallationOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/integrations/connect/register",
  });

  static async perform(
    args: RequestArgsOrigin & { input: RegisterConnectInstallationRequestBody },
  ): Promise<RegisterConnectInstallationResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <RegisterConnectInstallationResponseBody>(
      await resp.json()
    );
    return responseData;
  }
}

export type QueryConnectInstallationRequestBody = {
  connect_integration: QueryConnectInstallationInput;
};
export type QueryConnectInstallationResponseBody = {
  team?: Team;
  connect_integration: ConnectInstallation;
};

export class QueryConnectInstallationOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/integrations/connect/query",
  });

  static async perform(
    args: RequestArgsOrigin & { input: QueryConnectInstallationRequestBody },
  ): Promise<QueryConnectInstallationResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <QueryConnectInstallationResponseBody>(
      await resp.json()
    );
    return responseData;
  }
}
