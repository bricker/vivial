import { EaveConfig } from "@eave-fyi/eave-stdlib-ts/src/config.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";

export const GITHUB_EVENT_QUEUE_NAME = "github-events-processor";
export const API_BRANCH_NAME = "refs/heads/eave/auto-docs/api";

class AppConfig extends EaveConfig {
  eaveOrigin = EaveApp.eave_github_app;

  /**
   * Asynchronously retrieves the Eave Github Application ID from the secrets storage.
   * @returns {Promise<string>} A promise that resolves to the Eave Github Application ID.
   */
  get eaveGithubAppId(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_ID");
  }

  /**
   * Retrieves the secret key for the Eave Github App Webhook from the environment variables.
   * @returns {Promise<string>} A promise that resolves to the secret key as a string.
   */
  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_WEBHOOK_SECRET");
  }

  /**
   * Asynchronously retrieves the private key for the Eave Github application.
   * @returns {Promise<string>} A promise that resolves to the private key string.
   */
  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_PRIVATE_KEY");
  }

  /**
   * Retrieves the client ID of the Eave Github application.
   * This ID is stored as a secret and is returned as a Promise.
   * @returns {Promise<string>} A promise that resolves to the client ID of the Eave Github application.
   */
  get eaveGithubAppClientId(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_CLIENT_ID");
  }

  /**
   * Retrieves the client secret for the Eave Github App.
   * @returns {Promise<string>} A promise that resolves to the client secret.
   */
  get eaveGithubAppClientSecret(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_CLIENT_SECRET");
  }

  /**
   * Retrieves the secret key for the Eave Github App Cron job from the secret storage.
   * @returns {Promise<string>} A promise that resolves to the secret key as a string.
   */
  get eaveGithubAppCronSecret(): Promise<string> {
    return this.getSecret("EAVE_GITHUB_APP_CRON_SECRET");
  }
}

export const appConfig = new AppConfig();
