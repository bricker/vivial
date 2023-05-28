import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins';

class AppConfig extends EaveConfig {
  origin = EaveOrigin.eave_github_app;

  eaveGithubAppId = '300560';

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_WEBHOOK_SECRET');
  }

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_PRIVATE_KEY');
  }
}

export const appConfig = new AppConfig();
