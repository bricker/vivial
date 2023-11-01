// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
/* eslint-disable @typescript-eslint/no-unused-vars */
import { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import assert from "assert";
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import { loadStandardDotenvFiles } from "../../../../develop/javascript/dotenv-loader.cjs";
import { ExpressAPIDocumentBuilder } from "../../src/lib/api-documentation/builder.js";
import { CoreAPIData } from "../../src/lib/api-documentation/core-api.js";
import { GithubAPIData } from "../../src/lib/api-documentation/github-api.js";
import { compileQuery, graphql } from "../../src/lib/graphql-util.js";
import { createOctokitClient } from "../../src/lib/octokit-util.js";
import { generateExpressAPIDoc } from "../../src/tasks/run-api-documentation.js";

loadStandardDotenvFiles();

const externalRepoId = process.env["__EXTERNAL_REPO_ID"]!;
const teamId = process.env["__EAVE_TEAM_ID"]!;
const installationId = process.env["__INSTALLATION_ID"]!;

assert(externalRepoId, "__EXTERNAL_REPO_ID is required");
assert(teamId, "__EAVE_TEAM_ID is required");
assert(installationId, "__INSTALLATION_ID is required");

async function generateAPIDocs() {
  const octokit = await createOctokitClient(parseInt(installationId, 10));

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

      const newDocumentContents = await generateExpressAPIDoc({
        expressAPIInfo,
        ctx,
      });
      console.log(newDocumentContents);
    }),
  );
}

async function getPullRequestFiles() {
  const octokit = await createOctokitClient(parseInt(installationId, 10));
  const ctx = new LogContext();

  const githubAPIData = new GithubAPIData({
    ctx,
    octokit,
    externalRepoId,
  });

  const externalGithubRepo = await githubAPIData.getExternalGithubRepo();
  console.log("externalGithubRepo", externalGithubRepo);

  let query = await compileQuery(
    graphql(`
      query ($repoOwner: String!, $repoName: String!, $prNumber: Int!) {
        repository(owner: $repoOwner, name: $repoName) {
          pullRequest(number: $prNumber) {
            files(first: 100) {
              nodes {
                path
              }
            }

            title
            body
            headRefName
            headRef {
              target {
                __typename
                oid
              }
            }
          }
        }
      }
    `),
  );

  let r: any = await octokit.graphql(query, {
    repoOwner: externalGithubRepo.owner.login,
    repoName: externalGithubRepo.name,
    prNumber: 0, // FIXME
  });

  console.log(r);

  const headRefName = r.repository.pullRequest.headRefName;
  const filePaths = r.repository.pullRequest.files.nodes.map((n) => n.path);

  query = await compileQuery(
    graphql(`
      query ($repoOwner: String!, $repoName: String!, $expression: String!) {
        repository(owner: $repoOwner, name: $repoName) {
          object(expression: $expression) {
            __typename
            ... on Blob {
              text
            }
          }
        }
      }
    `),
  );

  for (const p of filePaths) {
    r = await octokit.graphql(query, {
      repoOwner: externalGithubRepo.owner.login,
      repoName: externalGithubRepo.name,
      expression: `${headRefName}:${p}`,
    });
    console.log(r);
  }
}

// void generateAPIDocs();
// void main();
