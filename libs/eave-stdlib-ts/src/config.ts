import { SecretManagerServiceClient } from '@google-cloud/secret-manager';
import { ProjectsClient } from '@google-cloud/compute';
import { CloudRedisClient } from '@google-cloud/redis';
import { google } from '@google-cloud/redis/build/protos/protos.js';

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
    return process.env['EAVE_MONITORING_ENABLED'] !== undefined;
  }

  get analyticsEnabled(): boolean {
    return process.env['EAVE_ANALYTICS_ENABLED'] !== undefined;
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

  async eaveApiBase(): Promise<string> {
    const k = 'EAVE_API_BASE';
    const v = process.env[k];
    if (v) {
      return v;
    } else {
      const metadata = await this.gcpMetadata();
      return metadata[k] || 'https://api.eave.fyi';
    }
  }

  async eaveWwwBase(): Promise<string> {
    const k = 'EAVE_WWW_BASE';
    const v = process.env[k];
    if (v) {
      return v;
    } else {
      const metadata = await this.gcpMetadata();
      return metadata[k] || 'https://www.eave.fyi';
    }
  }

  async eaveAppsBase(): Promise<string> {
    const k = 'EAVE_APPS_BASE';
    const v = process.env[k];
    if (v) {
      return v;
    } else {
      const metadata = await this.gcpMetadata();
      return metadata[k] || 'https://apps.eave.fyi';
    }
  }

  async eaveApexDomain(): Promise<string> {
    const www = await this.eaveWwwBase();
    const host = new URL(www).hostname;
    return host.replace(/^www\./, '');
  }

  async eaveCookieDomain(): Promise<string> {
    const v = await this.eaveApexDomain();
    return `.${v}`;
  }


  async redisInstance(): Promise<google.cloud.redis.v1.IInstance | undefined> {
    if (this.isDevelopment) {
      const host = process.env['REDIS_HOST'];
      if (host) {
        return {
          name: 'development',
          host,
          port: parseInt(process.env['REDIS_PORT'] || '6378', 10),
          transitEncryptionMode: google.cloud.redis.v1.Instance.TransitEncryptionMode.TRANSIT_ENCRYPTION_MODE_UNSPECIFIED,
          serverCaCerts: [],
        };
      } else {
        return undefined;
      }
    } else {
      const client = new CloudRedisClient();
      const instanceName = await this.redisInstanceName(client);
      const [instance] = await client.getInstance({
        name: instanceName,
      });
      return instance;
    }
  }

  async redisAuth(): Promise<string | undefined> {
    if (this.isDevelopment) {
      return process.env['REDIS_AUTH'];
    } else {
      const client = new CloudRedisClient();
      const instanceName = await this.redisInstanceName(client);
      const [authString] = await client.getInstanceAuthString({
        name: instanceName,
      });

      return authString.authString ? authString.authString : undefined;
    }
  }

  private async redisInstanceName(client: CloudRedisClient): Promise<string> {
    const instanceName = (await this.gcpMetadata())['REDIS_INSTANCE_ID'] || 'redis-core';
    return client.instancePath(
      this.googleCloudProject,
      'us-central1', // FIXME: hardcoded location value
      instanceName,
    );
  }

  async redisCacheDb(): Promise<string> {
    const k = 'REDIS_CACHE_DB';
    const v = process.env[k];
    if (v) {
      return v;
    } else {
      const metadata = await this.gcpMetadata();
      return metadata[k] || '0';
    }
  }

  get openaiApiKey(): Promise<string> {
    return this.getSecret('OPENAI_API_KEY');
  }

  get openaiApiOrg(): Promise<string> {
    return this.getSecret('OPENAI_API_ORG');
  }

  async gcpMetadata(): Promise<{[key:string]: string}> {
    const cacheKey = 'func_gcpMetadata';
    const cachedData = this.cache[cacheKey];
    if (cachedData) {
      return cachedData;
    }

    const client = new ProjectsClient();
    const [project] = await client.get({
      project: this.googleCloudProject,
    });

    const metadata = project.commonInstanceMetadata;
    if (!metadata || !metadata.items) {
      return {};
    }

    const table: {[key:string]: string} = {};
    metadata.items.forEach((item) => {
      const k = item.key;
      if (k) {
        table[k] = item.value;
      }
    });

    this.cache[cacheKey] = table;
    return table;
  }

  private cache: { [key: string]: any } = {};

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
