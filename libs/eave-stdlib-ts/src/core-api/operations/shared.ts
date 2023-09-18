import { sharedConfig } from "../../config.js";
import { EaveApp } from "../../eave-origins.js";

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export class CoreApiEndpointConfiguration {
  path: string;

  constructor({
    path,
  }: {
    path: string,
  }) {
    this.path = path;
  }

  get url(): string {
    return `${baseUrl}${this.path}`;
  }
}
