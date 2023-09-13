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
  repoName: string,
  repoOwner: string,
  repoId: string,
  baseBranchName: string,
  branchName: string,
  commitMessage: string,
  prTitle: string,
  prBody: string,
  fileChanges: Array<FileChange>,
}

export type CreateGitHubPullRequestResponseBody = {
  pr_number: number,
}
