import { VerifyInstallationRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/verify-installation.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { Request, Response } from "express";
import { Octokit } from "octokit";
import { appConfig } from "../config.js";
import { createOctokitClient } from "../lib/octokit-util.js";

/**
 * Manually verify a github app installation ID and OAuth user code
 * to try to protect against spoofed app install callback requests.
 * https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/about-the-setup-url
 *
 * Responds with 200 on successful verification, or 401 if verification failed.
 */
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

  // TODO: is there vulnerability in assuming this install id is ok to use for api auth??
  const octokit = await createOctokitClient(
    parseInt(input.installation_id, 10),
  );

  // TODO: test this result, no idea what the typing is on it
  // exchange code for an access token
  // https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/generating-a-user-access-token-for-a-github-app#generating-a-user-access-token-when-a-user-installs-your-app
  const {
    data: { accessToken },
  } = await octokit.request("POST /login/oauth/access_token", {
    client_id: appConfig.eaveGithubAppClientId,
    client_secret: appConfig.eaveGithubAppClientSecret,
    code: input.code,
    headers: {
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });

  // use access token to find list of installations the user has explicit access to
  // https://docs.github.com/en/rest/apps/installations?apiVersion=2022-11-28#list-app-installations-accessible-to-the-user-access-token
  const userOctokit = new Octokit({
    auth: accessToken,
  });

  const {
    data: { installations: accessibleInstallations },
  } = await userOctokit.request("GET /user/installations", {
    headers: {
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });

  // verify the provided installation is in that list
  const installation = accessibleInstallations.find(
    (install) => install.id.toString() === input.installation_id,
  );
  if (installation === undefined) {
    eaveLogger.warning(
      "Failed to find installation_id in list of accessible GitHub app installations",
      ctx,
    );
    res.sendStatus(401);
    return;
  }

  // verify the installation is an Eave app installation
  if (installation.app_id.toString() !== (await appConfig.eaveGithubAppId)) {
    eaveLogger.warning(
      "The installation_id was not an Eave GitHub app ID",
      ctx,
    );
    res.send(401);
    return;
  }

  res.sendStatus(200);
}
