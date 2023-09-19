import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GITHUB_APP_WEBHOOK_MOUNT_PATH, GITHUB_APP_TASKS_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export class GithubEventHandlerOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_WEBHOOK_MOUNT_PATH,
    subPath: "",
    authRequired: false,
    teamIdRequired: false,
    signatureRequired: false,
    originRequired: false,
  })
}