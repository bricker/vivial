import Express from "express";
import { sharedConfig } from "./config.js";
import { EaveApp } from "./eave-origins.js";
import { ExpressRoutingMethod } from "./types.js";

export interface ClientRequestParameters {
  path: string;
  method: ExpressRoutingMethod;
  audience: EaveApp;
  url: string;
}

export abstract class ClientApiEndpointConfiguration
  implements ClientRequestParameters
{
  path: string;
  method: ExpressRoutingMethod;
  abstract audience: EaveApp;

  get baseUrl(): string {
    return sharedConfig.eaveInternalServiceBase(this.audience);
  }

  get url(): string {
    return `${this.baseUrl}${this.path}`;
  }

  constructor({
    path,
    method = ExpressRoutingMethod.post,
  }: {
    path: string;
    method?: ExpressRoutingMethod;
  }) {
    this.path = path;
    this.method = method;
  }
}

export abstract class ServerApiEndpointConfiguration
  implements ClientRequestParameters
{
  path: string;
  method: ExpressRoutingMethod;
  teamIdRequired: boolean;
  authRequired: boolean;
  originRequired: boolean;
  signatureRequired: boolean;
  abstract audience: EaveApp;

  get baseUrl(): string {
    return sharedConfig.eaveInternalServiceBase(this.audience);
  }

  get url(): string {
    return `${this.baseUrl}${this.path}`;
  }

  abstract get middlewares(): Express.Handler[];

  constructor({
    path,
    method = ExpressRoutingMethod.post,
    teamIdRequired = true,
    authRequired = true,
    originRequired = true,
    signatureRequired = true,
  }: {
    path: string;
    method?: ExpressRoutingMethod;
    teamIdRequired?: boolean;
    authRequired?: boolean;
    originRequired?: boolean;
    signatureRequired?: boolean;
  }) {
    this.path = path;
    this.method = method;
    this.teamIdRequired = teamIdRequired;
    this.authRequired = authRequired;
    this.originRequired = originRequired;
    this.signatureRequired = signatureRequired;
  }
}
