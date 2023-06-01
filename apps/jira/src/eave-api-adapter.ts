import AddOnFactory from 'atlassian-connect-express';
import { queryJiraInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/jira.js';
import appConfig from './config.js';

type AppKey = "eave-confluence" | "eave-jira"
type ProductType = "confluence" | "jira"
type AdapterParams = { appKey: AppKey, productType: ProductType }

class EaveApiAdapter /* implements StoreAdapter */ {
  appKey: AppKey
  productType: ProductType

  constructor({appKey, productType}: AdapterParams) {
    this.appKey = appKey;
    this.productType = productType;
  }

  // FIXME: The `key` in this function params is usually `clientInfo`, which we can get from the API.
  // However, for OAuth, the key is dynamically generated using the user identifier and scopes.
  // So, this class is completely broken with OAuth.

  async get(key: string, clientKey: string): Promise<AddOnFactory.ClientInfo> {
    const response = await queryJiraInstallation({
      origin: appConfig.eaveOrigin,
      input: {
        jira_integration: {
          client_key: clientKey,
        },
      },
    });

    // The ClientInfo interface contains several properties which are non-nullable, but aren't needed for our purpose.
    // For those properties, we'll fill in with dummy values.
    return {
      key: this.appKey,
      productType: this.productType,
      clientKey: response.jira_integration.client_key,
      sharedSecret: response.jira_integration.shared_secret,
      baseUrl: response.jira_integration.base_url,
      description: '', // We actually have this, but it's not needed here.
      eventType: '',
      publicKey: '',
      serverVersion: '',
      pluginsVersion: '',
    }
  }

  async set(key: string, value: any, clientKey: string): Promise<any> {
  }

  async del(key: string, clientKey: string): Promise<void> {
  }

  async getAllClientInfos(): Promise<AddOnFactory.ClientInfo[]> {
    return [];
  }

  isMemoryStore() {
    return false;
  }
}

export default (logger: Console, opts: AdapterParams) => {
  return new EaveApiAdapter(opts);
}
