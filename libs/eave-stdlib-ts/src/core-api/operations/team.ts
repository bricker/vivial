import { RequestArgsAuthedRequest, makeRequest } from "../../requests.js";
import { GetTeamResponseBody } from "../models/team.js";
import { CoreApiEndpointClientConfiguration } from "./shared.js";

export class GetMyTeamRequest {
  static config = new CoreApiEndpointClientConfiguration({
    path: "/_/me/team/query",
    authRequired: true,
    originRequired: true,
  });

  static async perform(args: RequestArgsAuthedRequest): Promise<GetTeamResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetTeamResponseBody>await resp.json();
    return responseData;
  }
}
