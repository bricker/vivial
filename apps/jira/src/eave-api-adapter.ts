import AddOnFactory from 'atlassian-connect-express';
import { queryConnectInstallation, registerConnectInstallation, QueryConnectInstallationResponseBody } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import appConfig from './config.js';

type AppKey = 'eave-confluence' | 'eave-jira'
type AdapterParams = { appKey: AppKey, productType: AtlassianProduct }

class EaveApiAdapter /* implements StoreAdapter */ {
  appKey: AppKey;

  productType: AtlassianProduct;

  constructor({ appKey, productType }: AdapterParams) {
    this.appKey = appKey;
    this.productType = productType;
  }

  // FIXME: The `key` in this function params is usually `clientInfo`, which we can get from the API.
  // However, for OAuth, the key is dynamically generated using the user identifier and scopes.
  // So, this class is completely broken with OAuth.

  async get(key: string, clientKey: string): Promise<AddOnFactory.ClientInfo | null> {
    try {
      const response = await queryConnectInstallation({
        origin: appConfig.eaveOrigin,
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
    let parsedValue: AddOnFactory.ClientInfo;

    if (typeof value === 'string') {
      parsedValue = JSON.parse(value);
    } else {
      parsedValue = value;
    }

    const response = await registerConnectInstallation({
      origin: appConfig.eaveOrigin,
      input: {
        connect_integration: {
          product: this.productType,
          client_key: clientKey,
          base_url: parsedValue.baseUrl,
          shared_secret: parsedValue.sharedSecret,
          description: parsedValue.description,

        },
      },
    });

    return this.buildClientInfo(response);
  }

  async del(/* key: string, clientKey: string */): Promise<void> {
    // TODO: Fill in the delete function for Connect client info
  }

  async getAllClientInfos(): Promise<AddOnFactory.ClientInfo[]> {
    // TODO: Fill in the getAllClientInfos function
    return [];
  }

  isMemoryStore() {
    return false;
  }

  private buildClientInfo(response: QueryConnectInstallationResponseBody): AddOnFactory.ClientInfo {
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
