import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_confluence_app;
}

const appConfig = new AppConfig();
export default appConfig;
