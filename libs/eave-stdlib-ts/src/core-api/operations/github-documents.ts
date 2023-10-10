import { makeRequest, RequestArgsTeamId } from "../../requests.js";
import {
  GithubDocument,
  GithubDocumentCreateInput,
  GithubDocumentsDeleteByIdsInput,
  GithubDocumentsDeleteByTypeInput,
  GithubDocumentsQueryInput,
  GithubDocumentUpdateInput,
} from "../models/github-documents.js";
import { GithubRepo, GithubRepoRefInput } from "../models/github-repos.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type GetGithubDocumentsRequestBody = {
  query_params: GithubDocumentsQueryInput;
};

export type GetGithubDocumentsResponseBody = {
  documents: Array<GithubDocument>;
};

export class GetGithubDocumentsOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/github-documents/query",
  });
  static async perform(
    args: RequestArgsTeamId & { input: GetGithubDocumentsRequestBody },
  ): Promise<GetGithubDocumentsResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetGithubDocumentsResponseBody>await resp.json();
    return responseData;
  }
}
export type CreateGithubDocumentRequestBody = {
  repo: GithubRepoRefInput;
  document: GithubDocumentCreateInput;
};

export type CreateGithubDocumentResponseBody = {
  repo: GithubRepo;
  document: GithubDocument;
};

export class CreateGithubDocumentOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/github-documents/create",
  });
  static async perform(
    args: RequestArgsTeamId & { input: CreateGithubDocumentRequestBody },
  ): Promise<CreateGithubDocumentResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <CreateGithubDocumentResponseBody>await resp.json();
    return responseData;
  }
}
export type UpdateGithubDocumentRequestBody = {
  document: GithubDocumentUpdateInput;
};

export type UpdateGithubDocumentResponseBody = {
  document: GithubDocument;
};

export class UpdateGithubDocumentOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/github-documents/update",
  });
  static async perform(
    args: RequestArgsTeamId & { input: UpdateGithubDocumentRequestBody },
  ): Promise<UpdateGithubDocumentResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <UpdateGithubDocumentResponseBody>await resp.json();
    return responseData;
  }
}
export type DeleteGithubDocumentsByIdsRequestBody = {
  documents: Array<GithubDocumentsDeleteByIdsInput>;
};

export class DeleteGithubDocumentsByIdsOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/github-documents/delete/id",
  });
  static async perform(
    args: RequestArgsTeamId & {
      input: DeleteGithubDocumentsByIdsRequestBody;
    },
  ): Promise<void> {
    await makeRequest({
      config: this.config,
      ...args,
    });
  }
}
export type DeleteGithubDocumentsByTypeRequestBody = {
  documents: Array<GithubDocumentsDeleteByTypeInput>;
};

export class DeleteGithubDocumentsByTypeOperation {
  static config = new CoreApiEndpointConfiguration({
    path: "/github-documents/delete/type",
  });
  static async perform(
    args: RequestArgsTeamId & {
      input: DeleteGithubDocumentsByTypeRequestBody;
    },
  ): Promise<void> {
    await makeRequest({
      config: this.config,
      ...args,
    });
  }
}
