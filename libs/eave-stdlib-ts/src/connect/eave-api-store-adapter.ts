import AddOnFactory from "atlassian-connect-express";
import { Cache, getCacheClient } from "../cache.js";
import { AtlassianProduct } from "../core-api/models/connect.js";
import { QueryConnectInstallationOperation, QueryConnectInstallationResponseBody, RegisterConnectInstallationResponseBody } from "../core-api/operations/connect.js";
import { EaveApp } from "../eave-origins.js";
import { LogContext, eaveLogger } from "../logging.js";

type AppKey = "eave-confluence" | "eave-jira";
type AdapterParams = { appKey: AppKey; eaveOrigin: EaveApp; productType: AtlassianProduct };

export type EaveClientInfo = AddOnFactory.ClientInfo & {
  eaveTeamId?: string;
};

export class EaveApiAdapter /* implements StoreAdapter */ {
  appKey: AppKey;

  eaveOrigin: EaveApp;

  productType: AtlassianProduct;

  cacheKey(clientKey: string): string {
    return `confluence:${clientKey}:installation`;
  }

  async cacheClientInfo(clientKey: string, clientInfo: EaveClientInfo, ctx?: LogContext) {
    const cacheKey = this.cacheKey(clientInfo.clientKey);
    try {
      eaveLogger.debug(`[store adapter] writing cache entry: ${cacheKey}`, ctx);
      const cacheClient = await getCacheClient();
      await cacheClient.set(cacheKey, JSON.stringify(clientInfo));
    } catch (e: any) {
      eaveLogger.error(e);
    }
  }

  constructor({ appKey, eaveOrigin, productType }: AdapterParams) {
    this.appKey = appKey;
    this.productType = productType;
    this.eaveOrigin = eaveOrigin;
  }

  // FIXME: The `key` in this function params is usually `clientInfo`, which we can get from the API.
  // However, for OAuth, the key is dynamically generated using the user identifier and scopes.
  // So, this class is completely broken with OAuth, but we don't currently use OAuth in this context.

  async get(key: string, clientKey: string): Promise<AddOnFactory.ClientInfo | null> {
    eaveLogger.debug(`[store adapter] getting credentials: ${key}, ${clientKey}`);
    if (key !== "clientInfo") {
      throw new Error(`key not supported: ${key}`);
    }

    const cacheKey = this.cacheKey(clientKey);
    let cacheClient: Cache | undefined;
    try {
      cacheClient = await getCacheClient();
    } catch (e: any) {
      eaveLogger.error(e);
    }

    if (cacheClient !== undefined) {
      try {
        const cachedData = await cacheClient.get(cacheKey);
        if (cachedData) {
          const clientInfo = <EaveClientInfo>JSON.parse(cachedData.toString());
          eaveLogger.debug(`[store adapter] cache hit: ${cacheKey}`, <any>clientInfo);
          // Do some basic validation to make sure the cached data is valid.
          if (clientInfo.key && clientInfo.productType && clientInfo.clientKey && clientInfo.sharedSecret && clientInfo.baseUrl) {
            return clientInfo;
          } else {
            eaveLogger.warning(`[store adapter] Bad cache data: ${cacheKey}`);
            await cacheClient.del(cacheKey);
          }
        } else {
          eaveLogger.debug(`[store adapter] cache miss: ${cacheKey}`);
        }
      } catch (e: any) {
        eaveLogger.error(e);
        await cacheClient.del(cacheKey);
      }
    }

    try {
      const response = await QueryConnectInstallationOperation.perform({
        origin: this.eaveOrigin,
        input: {
          connect_integration: {
            product: this.productType,
            client_key: clientKey,
          },
        },
      });

      const clientInfo = this.buildClientInfo(response);
      await this.cacheClientInfo(clientKey, clientInfo);
      return clientInfo;
    } catch (e: any) {
      // HTTP error. Not Found is common, if the registration doesn't already exist.
      eaveLogger.debug(`[store adapter] no connect install exists (this is normal): ${key}, ${clientKey}`);
      return null;
    }
  }

  async set(key: string, value: string | AddOnFactory.ClientInfo, clientKey: string): Promise<any> {
    eaveLogger.debug(`[store adapter] setting client credentials: ${key}, ${value}, ${clientKey}`);
    if (key !== "clientInfo") {
      throw new Error(`key not supported: ${key}`);
    }

    let clientInfo: AddOnFactory.ClientInfo;
    if (typeof value === "string") {
      clientInfo = JSON.parse(value);
    } else {
      clientInfo = value;
    }
    await this.cacheClientInfo(clientKey, clientInfo);
  }

  async del(/* key: string, clientKey: string */): Promise<void> {
    eaveLogger.debug("[store adapter] del called");
    // TODO: Fill in the delete function for Connect client info
    // throw new Error('not implemented');
  }

  async getAllClientInfos(): Promise<AddOnFactory.ClientInfo[]> {
    eaveLogger.debug("[store adapter] getAllClientInfos called");
    return [];
    // TODO: Fill in the getAllClientInfos function
    // throw new Error('not implemented');
  }

  isMemoryStore() {
    return false;
  }

  private buildClientInfo(response: QueryConnectInstallationResponseBody | RegisterConnectInstallationResponseBody): EaveClientInfo {
    // The ClientInfo interface contains several properties which are non-nullable, but aren't needed for our purpose.
    // For those properties, we'll fill in with dummy values.
    return {
      eaveTeamId: response.team?.id,
      key: this.appKey,
      productType: this.productType,
      clientKey: response.connect_integration.client_key,
      sharedSecret: response.connect_integration.shared_secret,
      baseUrl: response.connect_integration.base_url,
      description: "", // We actually have this, but it's not needed here.
      eventType: "",
      publicKey: "",
      serverVersion: "",
      pluginsVersion: "",
    };
  }
}

export default (logger: Console, opts: AdapterParams) => {
  return new EaveApiAdapter(opts);
};
