import { EaveConfig } from '@eave-fyi/eave-stdlib-ts/src/config.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';

class AppConfig extends EaveConfig {
  eaveOrigin = EaveOrigin.eave_forge_app;

  webtriggerKey = 'webtrigger-eaveApi';

  // This needs to be overridden because the default implementation pulls from GCP, which is inaccessible here.
  override get eaveForgeAppSharedSecret(): Promise<string> {
    const v = process.env['EAVE_FORGE_SHARED_SECRET'];
    if (!v) {
      throw new Error('EAVE_FORGE_SHARED_SECRET not set');
    }
    return Promise.resolve(v);
  }

  get eaveGCPServiceAccountCredentials(): Buffer {
    const b64 = process.env['EAVE_GCP_SA_CREDENTIALS_B64'];
    if (!b64) {
      throw new Error('EAVE_GCP_SA_CREDENTIALS_B64 not set');
    }
    return Buffer.from(b64, 'base64');
  }

  get googleApplicationCredentialsFile(): string {
    const v = process.env['GOOGLE_APPLICATION_CREDENTIALS'] || 'gcp-app-creds.json';
    return v;
  }
}

const appConfig = new AppConfig();
export default appConfig;
