import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import { EaveService } from './eave-origins.js';

export enum EaveEnvironment {
  development = 'development',
  production = 'production',
}

export class EaveConfig {
  get googleCloudProject(): string {
    const value = process.env['GOOGLE_CLOUD_PROJECT'];
    if (value === undefined) {
      throw new Error('GOOGLE_CLOUD_PROJECT is undefined');
    }
    return value;
  }

  get devMode(): boolean {
    return this.nodeEnv === 'development';
  }

  get nodeEnv(): string {
    return process.env['NODE_ENV'] || 'production';
  }

  get eaveEnv(): EaveEnvironment {
    const strenv = process.env['EAVE_ENV'] || 'production';
    switch (strenv) {
      case 'development':
        return EaveEnvironment.development;
      case 'production':
        return EaveEnvironment.production;
      default:
        return EaveEnvironment.production;
    }
  }

  get isDevelopment(): boolean {
    return this.eaveEnv === EaveEnvironment.development;
  }

  get monitoringEnabled(): boolean {
    return process.env['EAVE_MONITORING_DISABLED'] !== '1';
  }

  get analyticsEnabled(): boolean {
    return process.env['EAVE_ANALYTICS_DISABLED'] !== '1';
  }

  get logLevel(): string {
    return (process.env['LOG_LEVEL'] || 'INFO').toLowerCase();
  }

  get appService(): string {
    return process.env['GAE_SERVICE'] || 'unknown';
  }

  get appVersion(): string {
    return process.env['GAE_VERSION'] || 'unknown';
  }

  get appLocation(): string {
    return process.env['GAE_LOCATION'] || 'us-central1';
  }

  get eavePublicAppsBase(): string {
    return process.env['EAVE_PUBLIC_APPS_BASE']
      || process.env['EAVE_APPS_BASE']
      || 'https://apps.eave.fyi';
  }

  get eavePublicApiBase(): string {
    return this.eavePublicServiceBase(EaveService.api);
  }

  get eavePublicWwwBase(): string {
    return this.eavePublicServiceBase(EaveService.www);
  }

  eavePublicServiceBase(service: EaveService): string {
    const envv = process.env[`EAVE_PUBLIC_${service.toUpperCase()}_BASE`];
    if (envv) {
      return envv;
    }

    switch (service) {
      case EaveService.api:
        return process.env['EAVE_API_BASE'] || 'https://api.eave.fyi';
      case EaveService.www:
        return process.env['EAVE_WWW_BASE'] || 'https://www.eave.fyi';
      default:
        return this.eavePublicAppsBase;
    }
  }

  eaveInternalServiceBase(service: EaveService): string {
    const envv = process.env[`EAVE_INTERNAL_${service.toUpperCase()}_BASE`];
    if (envv) {
      return envv;
    }

    if (this.isDevelopment) {
      switch (service) {
        case EaveService.api:
          return this.eavePublicApiBase;
        case EaveService.www:
          return this.eavePublicWwwBase;
        default:
          return this.eavePublicAppsBase;
      }
    } else {
      // FIXME: Hardcoded region id (uc)
      return `https://${service}-dot-${this.googleCloudProject}.uc.r.appspot.com`;
    }
  }

  get eaveCookieDomain(): string {
    const envv = process.env['EAVE_COOKIE_DOMAIN'];
    if (envv) {
      return envv;
    }

    const url = new URL(this.eavePublicWwwBase);
    return url.hostname.replace(/^www/, '');
  }

  get redisConnection(): {host: string, port: number, db: number} | undefined {
    const connection = process.env['REDIS_CONNECTION'];

    if (connection === undefined) {
      return undefined;
    }

    const parts = connection.split(':');

    const host = parts[0] || 'localhost';
    const port = parseInt(parts[1] || '6379', 10);
    const db = parseInt(parts[2] || '0', 10);
    return { host, port, db };
  }

  async redisAuth(): Promise<string | undefined> {
    const key = 'REDIS_AUTH';
    if (this.isDevelopment) {
      // Doing it this way because it would never make sense to use the gcloud secret in local dev.
      const value = process.env[key];
      return value;
    } else {
      try {
        const value = await this.getSecret(key);
        return value;
      } catch (e: unknown) {
        return undefined;
      }
    }
  }

  get redisTlsCA(): string | undefined {
    return process.env['REDIS_TLS_CA'];
  }

  get openaiApiKey(): Promise<string> {
    return this.getSecret('OPENAI_API_KEY');
  }

  get openaiApiOrg(): Promise<string> {
    return this.getSecret('OPENAI_API_ORG');
  }

  private cache: { [key: string]: string } = {};

  async getSecret(name: string): Promise<string> {
    const envValue = process.env[name];
    if (envValue !== undefined) {
      return envValue;
    }

    const cachedValue = this.cache[name];
    if (cachedValue !== undefined) {
      return cachedValue;
    }

    const client = new SecretManagerServiceClient();

    const qualifiedName = `projects/${this.googleCloudProject}/secrets/${name}/versions/latest`;
    const [version] = await client.accessSecretVersion({ name: qualifiedName });
    const value = version.payload?.data?.toString();
    if (value === undefined) {
      throw new Error(`secret not found: ${name}`);
    }

    this.cache[name] = value;
    return value;
  }
}

export const sharedConfig = new EaveConfig();
