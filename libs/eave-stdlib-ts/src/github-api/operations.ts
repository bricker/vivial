import { FileChange } from './models.js';

export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export type CreateGithubResourceSubscriptionRequestBody = {
  url: string;
}

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
