import { SecretManagerServiceClient } from "@google-cloud/secret-manager";
import { EaveApp } from "./eave-origins.js";

export enum EaveEnvironment {
  test = "test",
  development = "development",
  production = "production",
}

export class EaveConfig {
  get googleCloudProject(): string {
    const value = process.env["GOOGLE_CLOUD_PROJECT"];
    if (value === undefined) {
      throw new Error("GOOGLE_CLOUD_PROJECT is undefined");
    }
    return value;
  }

  get devMode(): boolean {
    return this.nodeEnv === "development";
  }

  get nodeEnv(): string {
    return process.env["NODE_ENV"] || "production";
  }

  get eaveEnv(): EaveEnvironment {
    const strenv = process.env["EAVE_ENV"] || "production";
    switch (strenv) {
      case "test":
        return EaveEnvironment.test;
      case "development":
        return EaveEnvironment.development;
      case "production":
        return EaveEnvironment.production;
      default:
        return EaveEnvironment.production;
    }
  }

  get isDevelopment(): boolean {
    return this.eaveEnv === EaveEnvironment.development;
  }

  get monitoringEnabled(): boolean {
    return process.env["EAVE_MONITORING_DISABLED"] !== "1";
  }

  get analyticsEnabled(): boolean {
    return process.env["EAVE_ANALYTICS_DISABLED"] !== "1";
  }

  get logLevel(): string {
    return (process.env["LOG_LEVEL"] || "INFO").toLowerCase();
  }

  get appService(): string {
    return process.env["GAE_SERVICE"] || "unknown";
  }

  get appVersion(): string {
    return process.env["GAE_VERSION"] || "unknown";
  }

  get appLocation(): string {
    return process.env["GAE_LOCATION"] || "us-central1";
  }

  get eavePublicApiBase(): string {
    return this.eavePublicServiceBase(EaveApp.eave_api);
  }

  get eavePublicDashboardBase(): string {
    return this.eavePublicServiceBase(EaveApp.eave_dashboard);
  }

  eavePublicServiceBase(service: EaveApp): string {
    const envv = process.env[`${service.toUpperCase()}_BASE_PUBLIC`];
    return envv || "";
  }

  eaveInternalServiceBase(service: EaveApp): string {
    const envv = process.env[`${service.toUpperCase()}_BASE_INTERNAL`];
    return envv || "";
  }

  get eaveCookieDomain(): string {
    const envv = process.env["EAVE_COOKIE_DOMAIN"];
    if (envv) {
      return envv;
    }

    const url = new URL(this.eavePublicDashboardBase);
    return url.hostname.replace(/^dashboard/, "");
  }

  async redisConnection(): Promise<
    { host: string; port: number; db: number } | undefined
  > {
    const key = "REDIS_HOST_PORT";

    let value: string | undefined;

    if (this.isDevelopment) {
      value = process.env[key];
      if (!value) {
        return undefined;
      }
    } else {
      try {
        value = await this.getSecret(key);
      } catch (e) {
        return undefined;
      }
    }

    const [splithost, splitport, splitdb] = value.split(":");
    const host = splithost || "localhost";
    const port = parseInt(splitport || "6379", 10);
    const db = parseInt(splitdb || "0", 10);
    return { host, port, db };
  }

  async redisAuth(): Promise<string | undefined> {
    const key = "REDIS_AUTH";

    if (this.isDevelopment) {
      // Doing it this way because it would never make sense to use the gcloud secret in local dev.
      return process.env[key];
    } else {
      try {
        return this.getSecret(key);
      } catch {
        return undefined;
      }
    }
  }

  async redisTlsCA(): Promise<string | undefined> {
    const key = "REDIS_TLS_CA";

    if (this.isDevelopment) {
      return process.env[key];
    } else {
      try {
        return this.getSecret(key);
      } catch {
        return undefined;
      }
    }
  }

  get openaiApiKey(): Promise<string> {
    return this.getSecret("OPENAI_API_KEY");
  }

  get openaiApiOrg(): Promise<string> {
    return this.getSecret("OPENAI_API_ORG");
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
