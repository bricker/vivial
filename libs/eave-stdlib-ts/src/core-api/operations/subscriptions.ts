import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { DocumentReference, DocumentReferenceInput, Subscription, SubscriptionInput } from "../models/subscriptions.js";
import { Team } from "../models/team.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type CreateSubscriptionRequestBody = {
  subscription: SubscriptionInput;
  document_reference?: DocumentReferenceInput;
};

export type CreateSubscriptionResponseBody = {
  team: Team;
  subscription: Subscription;
  document_reference?: DocumentReference;
};

export class CreateSubscriptionOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/subscriptions/create" });
  static async perform(args: RequestArgsTeamId & { input: CreateSubscriptionRequestBody }): Promise<CreateSubscriptionResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <CreateSubscriptionResponseBody>await resp.json();
    return responseData;
  }
}

export type DeleteSubscriptionRequestBody = {
  subscription: SubscriptionInput;
};

export class DeleteSubscriptionOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/subscriptions/delete" });
  static async perform(args: RequestArgsTeamId & { input: DeleteSubscriptionRequestBody }): Promise<null> {
    await makeRequest({
      config: this.config,
      ...args,
    });
    return null;
  }
}

export type GetSubscriptionRequestBody = {
  subscription: SubscriptionInput;
};

export type GetSubscriptionResponseBody = {
  team: Team;
  subscription?: Subscription;
  document_reference?: DocumentReference;
};

export class GetSubscriptionOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/subscriptions/query" });
  static async perform(args: RequestArgsTeamId & { input: GetSubscriptionRequestBody }): Promise<GetSubscriptionResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetSubscriptionResponseBody>await resp.json();
    return responseData;
  }
}
