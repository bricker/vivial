import { GithubAppEndpointConfiguration } from "./shared.js";

export class GithubEventHandlerTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/_/github/tasks/events",
    authRequired: false,
    teamIdRequired: false,
  });

  // static async perform(args: RequestArgsTeamId): Promise<void> {
  //   // TODO: Place task on queue
  // }
}
