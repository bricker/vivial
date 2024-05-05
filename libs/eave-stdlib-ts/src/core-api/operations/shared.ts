import { ApiEndpointClientConfiguration } from "../../api-util.js";
import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export class CoreApiEndpointClientConfiguration extends ApiEndpointClientConfiguration {
  audience = EaveApp.eave_api;

  get url(): string {
    return `${baseUrl}${this.path}`;
  }
}
