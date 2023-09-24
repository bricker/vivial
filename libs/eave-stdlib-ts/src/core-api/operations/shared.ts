import { ClientApiEndpointConfiguration } from "../../api-util.js";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export class CoreApiEndpointConfiguration extends ClientApiEndpointConfiguration {
  audience = EaveApp.eave_api;

  get url(): string {
    return `${baseUrl}${this.path}`;
  }
}
