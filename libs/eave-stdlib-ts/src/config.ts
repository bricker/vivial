import assert from 'node:assert';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

export enum EaveEnvironment {
  development = 'development',
  production = 'production',
}

export class EaveConfig {
  get googleCloudProject(): string {
    const value = process.env['GOOGLE_CLOUD_PROJECT'];
    assert(value !== undefined);
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
    return process.env['EAVE_MONITORING_ENABLED'] !== undefined;
  }

  get analyticsEnabled(): boolean {
    return process.env['EAVE_ANALYTICS_ENABLED'] !== undefined;
  }

  get logLevel(): string {
    return process.env['LOG_LEVEL'] || 'INFO';
  }

  get appService(): string {
    return process.env['GAE_SERVICE'] || 'unknown';
  }

  get appVersion(): string {
    return process.env['GAE_VERSION'] || 'unknown';
  }

  get eaveApiBase(): string {
    return process.env['EAVE_API_BASE'] || 'https://api.eave.fyi';
  }

  get eaveWwwBase(): string {
    return process.env['EAVE_WWW_BASE'] || 'https://www.eave.fyi';
  }

  get eaveAppsBase(): string {
    return process.env['EAVE_APPS_BASE'] || 'https://apps.eave.fyi';
  }

  get eaveCookieDomain(): string {
    return process.env['EAVE_COOKIE_DOMAIN'] || '.eave.fyi';
  }

  get openaiApiKey(): Promise<string> {
    return this.getSecret('OPENAI_API_KEY');
  }

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_WEBHOOK_SECRET');
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
    if (!value) {
      throw new Error(`secret not found: ${name}`);
    }

    this.cache[name] = value;
    return value;
  }
}

export const sharedConfig = new EaveConfig();
