import { webTrigger } from '@forge/api';
import { registerForgeInstallationInsecure } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/forge.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { InstalledAppEventPayload } from '../types.js';
import appConfig from '../config.js';

export default async function forgeInstalledAppEventHandler(event: InstalledAppEventPayload) {
  console.log('running forgeInstalledAppEventHandler');

  const webtriggerUrl = await webTrigger.getUrl(appConfig.webtriggerKey);
  console.log('got webtrigger URL', webtriggerUrl);
  const sharedSecret = await appConfig.eaveForgeAppSharedSecret;

  const resp = await registerForgeInstallationInsecure({
    origin: appConfig.eaveOrigin,
    sharedSecret,
    input: {
      forge_integration: {
        // atlassian_cloud_id: event.context?.cloudId, // TODO Add this to API input payload
        forge_app_id: event.app.id,
        forge_app_version: event.app.version,
        forge_app_installation_id: event.id,
        forge_app_installer_account_id: event.installerAccountId,
        webtrigger_url: webtriggerUrl,
      },
    },
  });

  console.log('received core API response', resp);
  eaveLogger.info('core API response', resp);
}
