import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_jira_app;

  // This is the same across all installations for the "eave-jira" app key
  eaveJiraAppAccountId = '712020:d50089b8-586c-4f54-a3ad-db70381e4cae';
}

const appConfig = new AppConfig();
export default appConfig;
