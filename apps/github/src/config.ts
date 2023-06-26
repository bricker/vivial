import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_github_app;

  eaveGithubAppId = '300560';

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_WEBHOOK_SECRET');
  }

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_PRIVATE_KEY');
  }

  get eaveGithubAppClientId(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_CLIENT_ID');
  }

  get eaveGithubAppClientSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_CLIENT_SECRET');
  }
}

export const appConfig = new AppConfig();
