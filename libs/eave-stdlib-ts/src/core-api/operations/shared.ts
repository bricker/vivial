import { ClientApiEndpointConfiguration, ServerApiEndpointConfiguration } from "../../api-util.js";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";
import { ExpressRoutingMethod } from "../../types.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export class CoreApiEndpointConfiguration extends ClientApiEndpointConfiguration {
  audience = EaveApp.eave_api;

  get url(): string {
    return `${baseUrl}${this.path}`;
  }
}
