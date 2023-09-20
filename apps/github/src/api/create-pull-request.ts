import { Request, Response } from 'express';
import { eaveLogger, LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { CreateGitHubPullRequestRequestBody, CreateGitHubPullRequestResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { getInstallationId, createOctokitClient } from '../lib/octokit-util.js';
import { PullRequestCreator } from '../lib/pull-request-creator.js';

export async function createPullRequestHandler(req: Request, res: Response): Promise<void> {
  const ctx = LogContext.load(res);
  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

  // validate input
  const input = <CreateGitHubPullRequestRequestBody>req.body;
  if (!(input.repo_name && input.repo_owner && input.repo_id
    && input.base_branch_name && input.branch_name && input.pr_body
    && input.pr_title && input.file_changes && input.commit_message)) {
    eaveLogger.error('Invalid input', ctx);
    res.sendStatus(400);
    return;
  }

  const installationId = await getInstallationId(eaveTeamId, ctx);
  if (installationId === null) {
    eaveLogger.error('missing github installation id', ctx);
    res.sendStatus(500);
    return;
  }
  const client = await createOctokitClient(installationId);

  const prCreator = new PullRequestCreator({
    repoName: input.repo_name,
    repoOwner: input.repo_owner,
    repoId: input.repo_id,
    baseBranchName: input.base_branch_name,
    octokit: client,
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
