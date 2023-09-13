import { Request, Response } from 'express';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { CreateGitHubPullRequestRequestBody, CreateGitHubPullRequestResponseBody } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { getInstallationId, createOctokitClient } from '../lib/octokit-util.js';
import { PullRequestCreator } from '../lib/pull-request-creator.js';

// TODO: create stdlib operations (ts and python)

export async function createPullRequest(req: Request, res: Response): Promise<void> {
  const ctx = LogContext.load(res);
  const eaveTeamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

  // validate input
  const input = <CreateGitHubPullRequestRequestBody>req.body;
  if (!(input.repoName && input.repoOwner && input.repoId
    && input.baseBranchName && input.branchName && input.prBody
    && input.prTitle && input.fileChanges && input.commitMessage)) {
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
    repoName: input.repoName,
    repoOwner: input.repoOwner,
    repoId: input.repoId,
    baseBranchName: input.baseBranchName, // TODO: does this also require the refs/heads prefix? 
    octokit: client,
    ctx,
  });
  const pr_number = await prCreator.createPullRequest({
    branchName: `refs/heads/${input.branchName}`,
    commitMessage: input.commitMessage,
    fileChanges: input.fileChanges,
    prTitle: input.prTitle,
    prBody: input.prBody,
  });

  const output: CreateGitHubPullRequestResponseBody = { pr_number };
  res.json(output);
}
