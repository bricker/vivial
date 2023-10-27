import { VerifyInstallationRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/verify-installation.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Query } from "@octokit/graphql-schema";
import { Request, Response } from "express";
import { Octokit } from "octokit";
import { appConfig } from "../config.js";
import { loadQuery } from "../lib/graphql-util.js";
import { createOctokitClient } from "../lib/octokit-util.js";

export async function verifyInstallation(
  req: Request,
  res: Response,
): Promise<void> {
  const ctx = LogContext.load(res);

  // validate input
  const input = <VerifyInstallationRequestBody>req.body;
  if (!(input.code && input.installation_id)) {
    eaveLogger.error("Invalid input", ctx);
    res.sendStatus(400);
    return;
  }

  const octokit = await createOctokitClient(
    parseInt(input.installation_id, 10),
  );

  // exchange code for an access token
  // https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#generating-a-user-access-token-when-a-user-installs-your-app
  // TODO: calidate this
  const { accessToken } = await octokit.request(
    "POST /login/oauth/access_token",
    {
      client_id: appConfig.eaveGithubAppClientId,
      client_secret: appConfig.eaveGithubAppClientSecret,
      code: input.code,
      headers: {
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );

  // validate access token has correct audience etc?

  // use access token to find list of installations the user has access to
  const userOctokit = new Octokit({
    auth: accessToken,
  });

  const accessibleInstallations = await userOctokit.request(
    "GET /user/installations",
    {
      headers: {
        "X-GitHub-Api-Version": "2022-11-28",
      },
    },
  );

  // verify installation_id is in that list

  // verify this is an Eave app installation id

  // 401 on failure?
  const query = await loadQuery("getRepos");
  const response = await octokit.graphql<{ viewer: Query["viewer"] }>(query);
  const repositories = response.viewer.repositories.nodes;

  res.sendStatus(200);
}
