import { ExpressRoutingMethod } from "../../types.js";
import { CoreApiEndpointClientConfiguration } from "./shared.js";

export type StatusResponseBody = {
  service: string;
  version: string;
  release_date: string; // underscore is to match python status payload
  status: string;
};

export class StatusOperation {
  static config = new CoreApiEndpointClientConfiguration({
    path: "/status",
    method: ExpressRoutingMethod.get,
    authRequired: false,
    originRequired: false,
  });

  static async perform(): Promise<StatusResponseBody> {
    const resp = await fetch(this.config.url, {
      method: ExpressRoutingMethod.get,
    });

    const responseData = <StatusResponseBody>await resp.json();
    return responseData;
  }
}
