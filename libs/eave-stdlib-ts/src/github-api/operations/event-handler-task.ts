import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GITHUB_APP_TASKS_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export class GithubEventHandlerTaskOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_TASKS_MOUNT_PATH,
    subPath: "/events",
    authRequired: false,
  })

  // static async perform(args: RequestArgsTeamId): Promise<void> {
  //   // TODO: Place task on queue
  // }
}