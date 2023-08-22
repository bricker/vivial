import process from 'node:process';
import { URL } from 'node:url';
import fs from 'node:fs/promises';
import path from 'node:path';
import { sharedConfig } from '../config.js';

export async function registerDevApp({ addon }: { addon: any }) {
  if (!sharedConfig.isDevelopment || !process.env['EAVE_HOME']) {
    return;
  }

  if (!process.env['AC_LOCAL_BASE_URL']) {
    try {
      // TODO: Make this path configurable
      const rawNgrokUrl = await fs.readFile(path.join(process.env['EAVE_HOME'], '.tmp/ngrokurl'), 'utf-8');
      console.debug(`running ngrok url: ${rawNgrokUrl}`);
      const configuredUrl = new URL(addon.config.localBaseUrl());
      const ngrokUrl = new URL(rawNgrokUrl);
      configuredUrl.protocol = ngrokUrl.protocol;
      configuredUrl.host = ngrokUrl.host;
      process.env['AC_LOCAL_BASE_URL'] = configuredUrl.toString();
      addon.reloadDescriptor();
    } catch {
      // Do nothing; ngrok isn't already running.
    }
  }

  await addon.register();
}
