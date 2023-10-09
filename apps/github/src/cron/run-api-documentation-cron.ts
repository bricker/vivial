import {
  Feature,
  State,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { GetAllTeamGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { EaveApp } from "@eave-fyi/eave-stdlib-ts/src/eave-origins.js";
import {
  RunApiDocumentationTaskOperation,
  RunApiDocumentationTaskRequestBody,
} from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { createTask } from "@eave-fyi/eave-stdlib-ts/src/task-queue.js";
import Express from "express";
import { GITHUB_EVENT_QUEUE_NAME, appConfig } from "../config.js";

export async function runApiDocumentationCronHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);

  const response = await GetAllTeamGithubReposOperation.perform({
    origin: appConfig.eaveOrigin,
    ctx,
    input: {
      query_params: {
        feature: Feature.API_DOCUMENTATION,
        state: State.ENABLED,
      },
    },
  });

  for (const repo of response.repos) {
    await createTask({
      payload: {
        repo: {
          external_repo_id: repo.external_repo_id,
        },
      } satisfies RunApiDocumentationTaskRequestBody, // This is for developers, to imply what the payload type is
      teamId: repo.team_id,
      queueName: GITHUB_EVENT_QUEUE_NAME,
      targetPath: RunApiDocumentationTaskOperation.config.path,
      origin: EaveApp.eave_github_app,
      audience: EaveApp.eave_github_app,
      ctx,
    });
  }
}
