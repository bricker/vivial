import { EaveConfig } from '@eave-fyi/eave-stdlib-ts';

class AppConfig extends EaveConfig {
  eaveGithubAppId = '300560';

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_WEBHOOK_SECRET');
  }

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_PRIVATE_KEY');
  }
}

export const appConfig = new AppConfig();
