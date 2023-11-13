import { makeRequest, RequestArgsTeamId } from "../../requests.js";
import {
  ApiDocumentationJob,
  ApiDocumentationJobListInput,
  ApiDocumentationJobUpsertInput,
} from "../models/api-documentation-jobs.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type GetApiDocumentationJobsRequestBody = {
  jobs?: ApiDocumentationJobListInput[];
};

export type GetApiDocumentationJobsResponseBody = {
  jobs: ApiDocumentationJob[];
};

export class GetApiDocumentationJobsOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/api-documentation-job/query",
  });
  static async perform(
    args: RequestArgsTeamId & { input: GetApiDocumentationJobsRequestBody },
  ): Promise<GetApiDocumentationJobsResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetApiDocumentationJobsResponseBody>await resp.json();
    return responseData;
  }
}

export type UpsertApiDocumentationJobRequestBody = {
  job: ApiDocumentationJobUpsertInput;
};

export type UpsertApiDocumentationJobResponseBody = {
  job: ApiDocumentationJob;
};

export class UpsertApiDocumentationJobOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/api-documentation-job/upsert",
  });
  static async perform(
    args: RequestArgsTeamId & { input: UpsertApiDocumentationJobRequestBody },
  ): Promise<UpsertApiDocumentationJobResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <UpsertApiDocumentationJobResponseBody>(
      await resp.json()
    );
    return responseData;
  }
}
