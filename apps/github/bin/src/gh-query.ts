import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import assert from "assert";
import { loadStandardDotenvFiles } from "../../../../develop/javascript/dotenv-loader.cjs";
import { ExpressAPIDocumentBuilder } from "../../src/lib/api-documentation/builder.js";
import { CoreAPIData } from "../../src/lib/api-documentation/core-api.js";
import { GithubAPIData } from "../../src/lib/api-documentation/github-api.js";
import { createOctokitClient } from "../../src/lib/octokit-util.js";

loadStandardDotenvFiles();

const externalRepoId = process.env["__EXTERNAL_REPO_ID"]!;
const teamId = process.env["__EAVE_TEAM_ID"]!;

assert(externalRepoId, "__EXTERNAL_REPO_ID is required");
assert(teamId, "__EAVE_TEAM_ID is required");

async function main() {
  const octokit = await createOctokitClient(43345876);

  const ctx = new LogContext();

  const githubAPIData = new GithubAPIData({
    ctx,
    octokit,
    externalRepoId,
  });

  const coreAPIData = new CoreAPIData({
    teamId,
    ctx,
    externalRepoId,
  });

  const externalGithubRepo = await githubAPIData.getExternalGithubRepo();
  console.log("externalGithubRepo", externalGithubRepo);

  const expressRootDirs = await githubAPIData.getExpressRootDirs();
  console.log("expressRootDirs", expressRootDirs);

  await Promise.all(
    expressRootDirs.map(async (apiRootDir) => {
      const expressAPIInfo = await ExpressAPIDocumentBuilder.buildAPI({
        githubAPIData,
        coreAPIData,
        apiRootDir,
        ctx,
      });

      console.log(expressAPIInfo);
    }),
  );
}

void main();
