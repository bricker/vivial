import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { FileChange } from "../models.js";
import { GITHUB_APP_API_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export type CreateGitHubPullRequestRequestBody = {
  repo_name: string,
  repo_owner: string,
  repo_id: string,
  base_branch_name: string,
  branch_name: string,
  commit_message: string,
  pr_title: string,
  pr_body: string,
  file_changes: Array<FileChange>,
}

export type CreateGitHubPullRequestResponseBody = {
  pr_number: number,
}

export class CreateGithubPullRequestOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_API_MOUNT_PATH,
    subPath: "/create-pull-request",
    authRequired: false,
  })

  static async perform(args: RequestArgsTeamId & {
    input: CreateGitHubPullRequestRequestBody,
  }): Promise<CreateGitHubPullRequestResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <CreateGitHubPullRequestResponseBody>(await resp.json());
    return responseData;
  }

}
