import { makeRequest, RequestArgsAuthedRequest, RequestArgsTeamId } from "../../requests.js";
import { GithubRepo, GithubRepoCreateInput, GithubRepoListInput, GithubReposDeleteInput, GithubReposFeatureStateInput, GithubRepoUpdateInput } from "../models/github-repos.js";
import { CoreApiEndpointConfiguration } from "./shared.js";

export type GetGithubReposRequestBody = {
  repos?: Array<GithubRepoListInput>;
};

export type GetGithubReposResponseBody = {
  repos: Array<GithubRepo>;
};

export class GetGithubReposOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/github-repos/query" });
  static async perform(args: RequestArgsTeamId & { input: GetGithubReposRequestBody }): Promise<GetGithubReposResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <GetGithubReposResponseBody>await resp.json();
    return responseData;
  }
}
export type FeatureStateGithubReposRequestBody = {
  query_params: GithubReposFeatureStateInput;
};

export type FeatureStateGithubReposResponseBody = {
  states_match: boolean;
};

export class FeatureStateGithubReposOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/github-repos/query/enabled" });
  static async perform(args: RequestArgsTeamId & { input: FeatureStateGithubReposRequestBody }): Promise<FeatureStateGithubReposResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <FeatureStateGithubReposResponseBody>await resp.json();
    return responseData;
  }
}
export type CreateGithubRepoRequestBody = {
  repo: GithubRepoCreateInput;
};

export type CreateGithubRepoResponseBody = {
  repo: GithubRepo;
};

export class CreateGithubRepoOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/github-repos/create" });
  static async perform(args: RequestArgsTeamId & { input: CreateGithubRepoRequestBody }): Promise<CreateGithubRepoResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <CreateGithubRepoResponseBody>await resp.json();
    return responseData;
  }
}
export type DeleteGithubReposRequestBody = {
  repos: Array<GithubReposDeleteInput>;
};

export class DeleteGithubRepoOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/github-repos/delete" });
  static async perform(args: RequestArgsTeamId & { input: DeleteGithubReposRequestBody }): Promise<void> {
    await makeRequest({
      config: this.config,
      ...args,
    });
  }
}

export type UpdateGithubReposRequestBody = {
  repos: Array<GithubRepoUpdateInput>;
};

export type UpdateGithubReposResponseBody = {
  repos: Array<GithubRepo>;
};

export class UpdateGithubReposOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/github-repos/update" });
  static async perform(args: RequestArgsAuthedRequest & { input: UpdateGithubReposRequestBody }): Promise<UpdateGithubReposResponseBody> {
    const resp = await makeRequest({
      config: this.config,
      ...args,
    });
    const responseData = <UpdateGithubReposResponseBody>await resp.json();
    return responseData;
  }
}
