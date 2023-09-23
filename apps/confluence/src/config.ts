import { EaveConfig } from "@eave-fyi/eave-stdlib-ts/src/config.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";

class AppConfig extends EaveConfig {
  eaveOrigin = EaveApp.eave_confluence_app;

  // This is the same across all installations for the "eave-confluence" app key
  eaveConfluenceAppAccountId = "712020:09cf9e48-97bd-4d65-b970-3538514d1358";
}

const appConfig = new AppConfig();
export default appConfig;
