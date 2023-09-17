import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { FileChange } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export const config = new GithubAppEndpointConfiguration({
  path: "/github/api/create-pull-request",
  authRequired: false,
})

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


export async function createGithubPullRequest(args: RequestArgsTeamId & {
  input: CreateGitHubPullRequestRequestBody,
}): Promise<CreateGitHubPullRequestResponseBody> {
  const resp = await makeRequest({
    url: config.url,
    ...args,
  });
  const responseData = <CreateGitHubPullRequestResponseBody>(await resp.json());
  return responseData;
}
