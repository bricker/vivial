import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { Team } from "../models/team.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type GetTeamResponseBody = {
  team: Team;
};

export class GetTeamOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/team/query" });

  static async perform(args: RequestArgsTeamId): Promise<GetTeamResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetTeamResponseBody>await resp.json();
    return responseData;
  }
}
