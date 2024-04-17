import { ExpressRoutingMethod } from "../../types.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type StatusResponseBody = {
  service: string;
  version: string;
  release_date: string; // underscore is to match python status payload
  status: string;
};

export class StatusOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/status",
    method: ExpressRoutingMethod.get,
    teamIdRequired: false,
    authRequired: false,
    originRequired: false,
    signatureRequired: false,
  });

  static async perform(): Promise<StatusResponseBody> {
    const resp = await fetch(this.config.url, {
      method: ExpressRoutingMethod.get,
    });

    const responseData = <StatusResponseBody>await resp.json();
    return responseData;
  }
}
