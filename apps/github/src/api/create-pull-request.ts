import { Request, Response } from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { CreateGitHubPullRequestRequestBody, CreateGitHubPullRequestResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js';
import { PullRequestCreator } from '../lib/pull-request-creator.js';
import { GitHubOperationsContext } from '../types.js';

export async function createPullRequest(
  req: Request, res: Response, context: GitHubOperationsContext
): Promise<void> {
  const { octokit, ctx } = context;

  // validate input
  const input = <CreateGitHubPullRequestRequestBody>req.body;
  if (!(input.repo_name && input.repo_owner && input.repo_id
    && input.base_branch_name && input.branch_name && input.pr_body
    && input.pr_title && input.file_changes && input.commit_message)) {
    eaveLogger.error('Invalid input', ctx);
    res.sendStatus(400);
    return;
  }

  const prCreator = new PullRequestCreator({
    repoName: input.repo_name,
    repoOwner: input.repo_owner,
    repoId: input.repo_id,
    baseBranchName: input.base_branch_name,
    octokit,
    ctx,
  });
  const pr_number = await prCreator.createPullRequest({
    branchName: input.branch_name,
    commitMessage: input.commit_message,
    fileChanges: input.file_changes,
    prTitle: input.pr_title,
    prBody: input.pr_body,
  });

  const output: CreateGitHubPullRequestResponseBody = { pr_number };
  res.json(output);
}
