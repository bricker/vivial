import { EaveConfig } from "@eave-fyi/eave-stdlib-ts/src/config.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";

export const GITHUB_EVENT_QUEUE_NAME = "github-events-processor";

class AppConfig extends EaveConfig {
  eaveOrigin = EaveApp.eave_github_app;

  get eaveGithubAppId(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_ID");
  }

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_WEBHOOK_SECRET");
  }

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_PRIVATE_KEY");
  }

  get eaveGithubAppClientId(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_CLIENT_ID");
  }

  get eaveGithubAppClientSecret(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_CLIENT_SECRET");
  }
}

export const appConfig = new AppConfig();
