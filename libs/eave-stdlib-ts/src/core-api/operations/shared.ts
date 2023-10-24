import { ClientApiEndpointConfiguration } from "../../api-types.js";
import { EaveApp } from "../../eave-origins.js";

export class CoreApiEndpointConfiguration extends ClientApiEndpointConfiguration {
  audience = EaveApp.eave_api;
}
