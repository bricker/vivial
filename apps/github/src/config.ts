import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config';

class AppConfig extends EaveConfig {
  eaveGithubAppId = '300560';

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_PRIVATE_KEY');
  }
}

export const appConfig = new AppConfig();
