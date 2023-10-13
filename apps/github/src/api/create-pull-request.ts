import {
  CreateGitHubPullRequestRequestBody,
  CreateGitHubPullRequestResponseBody,
} from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/create-pull-request.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Request, Response } from "express";
import { createTeamOctokitClient } from "../lib/octokit-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";

/**
 * Handles the creation of a new GitHub pull request.
 *
 * @param req - The incoming request object, expected to contain necessary pull request details in the body.
 * @param res - The outgoing response object.
 *
 * The request body should contain the following properties:
 * - repo_name: The name of the repository where the pull request will be created.
 * - repo_owner: The owner of the repository.
 * - repo_id: The ID of the repository.
 * - base_branch_name: The name of the base branch for the pull request.
 * - branch_name: The name of the branch where changes have been made.
 * - pr_body: The body content of the pull request.
 * - pr_title: The title of the pull request.
 * - file_changes: The changes made to the files.
 * - commit_message: The commit message.
 *
 * If the pull request is successfully created, the response will contain the pull request number.
 * If the pull request creation fails, a 400 status code will be returned.
 *
 * @returns A promise that resolves to void.
 */
export async function createPullRequestHandler(
  req: Request,
  res: Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const octokit = await createTeamOctokitClient(req, ctx);

  // validate input
  const input = <CreateGitHubPullRequestRequestBody>req.body;
  if (
    !(
      input.repo_name &&
      input.repo_owner &&
      input.repo_id &&
      input.base_branch_name &&
      input.branch_name &&
      input.pr_body &&
      input.pr_title &&
      input.file_changes &&
      input.commit_message
    )
  ) {
    eaveLogger.error("Invalid input", ctx);
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
  const pr = await prCreator.createPullRequest({
    branchName: input.branch_name,
    commitMessage: input.commit_message,
    fileChanges: {
      additions: input.file_changes,
    },
    prTitle: input.pr_title,
    prBody: input.pr_body,
  });

  const output: CreateGitHubPullRequestResponseBody = { pr_number: pr.number };
  res.json(output);
}
