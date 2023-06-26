import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_jira_app;

  eaveJiraAppKey = process.env['EAVE_JIRA_APP_KEY'] || 'eave-jira';

  eaveJiraAppName = process.env['EAVE_JIRA_APP_NAME'] || 'Eave for Jira';
}

const appConfig = new AppConfig();
export default appConfig;
