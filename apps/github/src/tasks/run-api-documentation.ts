import { RunApiDocumentationTaskRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import Express from "express";

export async function runApiDocumentationTaskHandler(req: Express.Request, res: Express.Response): Promise<void> {
  const ctx = LogContext.load(res);
  const input = <RunApiDocumentationTaskRequestBody>req.body;

  /**
   * TODO:
   * 1. Get the team given by eave-team-id header
   * 1. Get the full GithubRepo object from Core API using external_repo_id (body) and eave-team-id (header)
   * 1. Verify that the feature is enabled
   * 1. Create container GithubDocument with default state
   * 1. Run the API documentation process
   * 1. Open a pull request
   * 1. Update the GithubDocument object with the PR number
   */
}
