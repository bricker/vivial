import assert from 'node:assert';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

class Config {
  get googleCloudProject(): string {
    const value = process.env['GOOGLE_CLOUD_PROJECT'];
    assert(value !== undefined);
    return value;
  }

  get nodeEnv(): string {
    return process.env['NODE_ENV'] || 'development';
  }

  eaveGithubAppId = '300560';

  get eaveApiBase(): string {
    const value = process.env['EAVE_API_BASE'];
    assert(value !== undefined);
    return value;
  }

  get openaiApiKey(): Promise<string> {
    return this.getSecret('OPENAI_API_KEY');
  }

  get eaveSigningSecret(): Promise<string> {
    return this.getSecret('EAVE_SIGNING_SECRET');
  }

  get eaveGithubAppWebhookSecret(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_WEBHOOK_SECRET');
  }

  get eaveGithubAppPrivateKey(): Promise<string> {
    return this.getSecret('EAVE_GITHUB_APP_PRIVATE_KEY');
  }

  async getSecret(name: string): Promise<string> {
    const envValue = process.env[name];
    if (envValue !== undefined) {
      return envValue;
    }

    const client = new SecretManagerServiceClient();

    const qualifiedName = `projects/${this.googleCloudProject}/secrets/${name}/versions/latest`;
    const [version] = await client.accessSecretVersion({ name: qualifiedName });
    const value = version.payload?.data?.toString();
    if (!value) {
      throw new Error(`secret not found: ${name}`);
    }
    return value;
  }
}

const appConfig = new Config();
export default appConfig;
