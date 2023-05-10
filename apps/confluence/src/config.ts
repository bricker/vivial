import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config';

class AppConfig extends EaveConfig {
  eaveForgeAppId = '8ce7aa2c-a5eb-4e6c-aff2-52b7cb4803d9';

  eaveCoreApiUrl = 'https://api.eave.fyi';
}

const appConfig = new AppConfig();
export default appConfig;
