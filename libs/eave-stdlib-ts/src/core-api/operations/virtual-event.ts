import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import {
  VirtualEvent,
  VirtualEventQueryInput,
} from "../models/virtual-event.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type GetVirtualEventsRequestBody = {
  virtual_events?: VirtualEventQueryInput;
};

export type GetVirtualEventsResponseBody = {
  virtual_events: Array<VirtualEvent>;
};

export class GetVirtualEventsRequest {
  static config = new CoreApiEndpointConfiguration({
    path: "/_/virtual-events/query",
    signatureRequired: false,
  });

  static async perform(
    args: RequestArgsTeamId & { input: GetVirtualEventsRequestBody },
  ): Promise<GetVirtualEventsResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetVirtualEventsResponseBody>await resp.json();
    return responseData;
  }
}
