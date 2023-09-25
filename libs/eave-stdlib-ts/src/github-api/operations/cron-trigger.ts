import { GithubAppEndpointConfiguration } from "./shared.js";

export class CronTriggerOperation {
  static config = new GithubAppEndpointConfiguration({
    path: "/_/github/cron",
    authRequired: false,
    teamIdRequired: false,
    originRequired: false,
    signatureRequired: false,
  });
}
