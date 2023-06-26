import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_confluence_app;

  eaveConfluenceAppKey = process.env['EAVE_CONFLUENCE_APP_KEY'] || 'eave-confluence';

  eaveConfluenceAppName = process.env['EAVE_CONFLUENCE_APP_NAME'] || 'Eave for Confluence';
}

const appConfig = new AppConfig();
export default appConfig;
