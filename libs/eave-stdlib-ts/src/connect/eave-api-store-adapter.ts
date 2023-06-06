import AddOnFactory from 'atlassian-connect-express';
import { queryConnectInstallation, registerConnectInstallation, QueryConnectInstallationResponseBody, RegisterConnectInstallationResponseBody } from '../core-api/operations/connect.js';
import { AtlassianProduct } from '../core-api/models/connect.js';
import { EaveOrigin } from '../eave-origins.js';

type AppKey = 'eave-confluence' | 'eave-jira'
type AdapterParams = { appKey: AppKey, eaveOrigin: EaveOrigin, productType: AtlassianProduct }

class EaveApiAdapter /* implements StoreAdapter */ {
  appKey: AppKey;

  eaveOrigin: EaveOrigin;

  productType: AtlassianProduct;

  constructor({ appKey, eaveOrigin, productType }: AdapterParams) {
    this.appKey = appKey;
    this.productType = productType;
    this.eaveOrigin = eaveOrigin;
  }

  // FIXME: The `key` in this function params is usually `clientInfo`, which we can get from the API.
  // However, for OAuth, the key is dynamically generated using the user identifier and scopes.
  // So, this class is completely broken with OAuth, but we don't currently use OAuth in this context.

  async get(key: string, clientKey: string): Promise<AddOnFactory.ClientInfo | null> {
    try {
      const response = await queryConnectInstallation({
        origin: this.eaveOrigin,
        input: {
          connect_integration: {
            product: this.productType,
            client_key: clientKey,
          },
        },
      });

      return this.buildClientInfo(response);
    } catch (e: any) {
      // HTTP error. Not Found is common, if the registration doesn't already exist.
      return null;
    }
  }

  async set(key: string, value: string | AddOnFactory.ClientInfo, clientKey: string): Promise<any> {
    throw new Error('not implemented');
  }

  async del(/* key: string, clientKey: string */): Promise<void> {
    // TODO: Fill in the delete function for Connect client info
    throw new Error('not implemented');
  }

  async getAllClientInfos(): Promise<AddOnFactory.ClientInfo[]> {
    // TODO: Fill in the getAllClientInfos function
    throw new Error('not implemented');
  }

  isMemoryStore() {
    return false;
  }

  private buildClientInfo(response: QueryConnectInstallationResponseBody | RegisterConnectInstallationResponseBody): AddOnFactory.ClientInfo {
    // The ClientInfo interface contains several properties which are non-nullable, but aren't needed for our purpose.
    // For those properties, we'll fill in with dummy values.
    return {
      key: this.appKey,
      productType: this.productType,
      clientKey: response.connect_integration.client_key,
      sharedSecret: response.connect_integration.shared_secret,
      baseUrl: response.connect_integration.base_url,
      description: '', // We actually have this, but it's not needed here.
      eventType: '',
      publicKey: '',
      serverVersion: '',
      pluginsVersion: '',
    };
  }
}

export default (logger: Console, opts: AdapterParams) => {
  return new EaveApiAdapter(opts);
};
