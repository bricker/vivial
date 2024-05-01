import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import {
  GetVirtualEventsRequestBody,
  GetVirtualEventsResponseBody,
} from "../models/virtual-event.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

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
