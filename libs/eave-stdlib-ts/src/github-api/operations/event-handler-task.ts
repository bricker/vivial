import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export class GithubEventHandlerTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/_/github/events",
    authRequired: false,
  })

  // static async perform(args: RequestArgsTeamId): Promise<void> {
  //   // TODO: Place task on queue
  // }
}