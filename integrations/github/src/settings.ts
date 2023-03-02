import assert from 'node:assert';
import { SecretManagerServiceClient } from '@google-cloud/secret-manager';

class Settings {
  get googleCloudProject(): string {
    const value = process.env['GOOGLE_CLOUD_PROJECT'];
    assert(value !== undefined);
    return value;
  }

  get nodeEnv(): string {
    return process.env['NODE_ENV'] || 'development';
  }

  eaveGithubAppId = '300560';

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

const appSettings = new Settings();
export default appSettings;
