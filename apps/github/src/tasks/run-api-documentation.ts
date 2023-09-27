import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { ExpressAPIDocumentor } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-api-documentor.js";
import {
  DocumentType,
  GithubDocument,
  GithubDocumentValuesInput,
  Status,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import {
  GithubRepo,
  State,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  CreateGithubDocumentOperation,
  GetGithubDocumentsOperation,
  UpdateGithubDocumentOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-documents.js";
import { GetGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { GetTeamOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js";
import { MissingRequiredHeaderError } from "@eave-fyi/eave-stdlib-ts/src/exceptions.js";
import { RunApiDocumentationTaskRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { EAVE_TEAM_ID_HEADER } from "@eave-fyi/eave-stdlib-ts/src/headers.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { Query, Repository, Scalars } from "@octokit/graphql-schema";
import assert from "assert";
import Express from "express";
import { appConfig } from "../config.js";
import { loadQuery } from "../lib/graphql-util.js";
import { createOctokitClient, getInstallationId } from "../lib/octokit-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";
import { GitHubOperationsContext } from "../types.js";

export async function runApiDocumentationTaskHandler(
  req: Express.Request,
  res: Express.Response,
): Promise<void> {
  const ctx = LogContext.load(res);
  const input = <RunApiDocumentationTaskRequestBody>req.body;

  const teamId = req.header(EAVE_TEAM_ID_HEADER);
  if (!teamId) {
    throw new MissingRequiredHeaderError(EAVE_TEAM_ID_HEADER);
  }

  const team = await getTeam({ teamId, ctx });
  const installId = await getInstallationId(team.id, ctx);
  assert(installId, `No github integration found for team ID ${team.id}`);

  const octokit = await createOctokitClient(installId);

  const repo = await getRepo({ team, input, ctx });
  assert(
    repo.api_documentation_state === State.ENABLED,
    `API documentation feature not enabled for repo ID ${repo.external_repo_id}`,
  );

  await logEvent({
    event_name: "run_api_documentation",
    event_description:
      "The API documentation process was kicked off for a repo",
    eave_team: team,
    event_source: "github app",
    opaque_params: {
      repo,
    },
  });

  const document = await getOrCreateGithubDocument({ repo, team, ctx });

  const externalRepo = await getExternalRepo({ repo, octokit, ctx });
  const documentor = new ExpressAPIDocumentor(repo, ctx);
  const newDocumentContent = await documentor.document();

  const prCreator = new PullRequestCreator({
    repoName: externalRepo.name,
    repoOwner: externalRepo.owner.login,
    repoId: externalRepo.id,
    baseBranchName: externalRepo.defaultBranchRef?.name || "main", // The only reason `defaultBranchRef` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
    octokit,
    ctx,
  });

  const filePath = "EAVE_DOCS.md";
  const pullRequest = await prCreator.createPullRequest({
    branchName: "refs/heads/eave/auto-docs/api",
    commitMessage: "docs: automated update",
    fileChanges: [
      {
        path: filePath,
        contents: Buffer.from(newDocumentContent).toString("base64"),
      },
    ],
    prTitle: "docs: Eave API documentation update",
    prBody: "Your new API docs based on recent changes to your code",
  });

  await updateGithubDocument({
    newValues: {
      pull_request_number: pullRequest.number,
      status: Status.PR_OPENED,
      api_name: "tktktktk",
      file_path: "tktktktkt",
    },
    document,
    team,
    ctx,
  });
}

async function getTeam({
  teamId,
  ctx,
}: CtxArg & { teamId: string }): Promise<Team> {
  const response = await GetTeamOperation.perform({
    origin: appConfig.eaveOrigin,
    teamId,
    ctx,
  });
  return response.team;
}

async function getRepo({
  team,
  input,
  ctx,
}: CtxArg & {
  team: Team;
  input: RunApiDocumentationTaskRequestBody;
}): Promise<GithubRepo> {
  const response = await GetGithubReposOperation.perform({
    origin: appConfig.eaveOrigin,
    teamId: team.id,
    input: {
      repos: [input.repo],
    },
    ctx,
  });

  if (response.repos.length > 1) {
    eaveLogger.warning(
      `Unexpected multiple repos for id ${input.repo.external_repo_id}`,
      ctx,
    );
  }

  const repo = response.repos[0];
  assert(repo, `No repo found in Eave for ID ${input.repo.external_repo_id}`);
  return repo;
}

async function getOrCreateGithubDocument({
  team,
  repo,
  ctx,
}: CtxArg & { team: Team; repo: GithubRepo }): Promise<GithubDocument> {
  const getDocResponse = await GetGithubDocumentsOperation.perform({
    input: {
      query_params: {
        external_repo_id: repo.external_repo_id,
        type: DocumentType.API_DOCUMENT,
      },
    },
    origin: appConfig.eaveOrigin,
    teamId: team.id,
    ctx,
  });

  if (getDocResponse.documents.length > 1) {
    eaveLogger.warning(
      `Unexpected multiple documents for repo id ${repo.external_repo_id}`,
      ctx,
    );
  }

  const existingDocument = getDocResponse.documents[0];
  if (existingDocument) {
    return existingDocument;
  }

  const createDocResponse = await CreateGithubDocumentOperation.perform({
    origin: appConfig.eaveOrigin,
    ctx,
    teamId: team.id,
    input: {
      document: {
        external_repo_id: repo.external_repo_id,
        type: DocumentType.API_DOCUMENT,
        api_name: null,
        file_path: null,
        pull_request_number: null,
      },
    },
  });

  return createDocResponse.document;
}

async function updateGithubDocument({
  team,
  document,
  newValues,
  ctx,
}: CtxArg & {
  team: Team;
  document: GithubDocument;
  newValues: GithubDocumentValuesInput;
}): Promise<void> {
  await UpdateGithubDocumentOperation.perform({
    input: {
      document: {
        id: document.id,
        new_values: newValues,
      },
    },
    origin: appConfig.eaveOrigin,
    teamId: team.id,
    ctx,
  });
}

async function getExternalRepo({
  repo,
  ctx,
  octokit,
}: GitHubOperationsContext & { repo: GithubRepo }): Promise<Repository> {
  const query = await loadQuery("getRepo");
  const variables: {
    nodeId: Scalars["ID"]["input"];
  } = {
    nodeId: repo.external_repo_id,
  };

  const response = await octokit.graphql<{ node: Query["node"] }>(
    query,
    variables,
  );
  return <Repository>response.node;
}

async function generateApiDocumentation({
  repo,
  octokit,
  ctx,
}: GitHubOperationsContext & { repo: Repository }) {
  const response = await octokit.rest.search.code({
    q: encodeURIComponent(
      `"express": in:file filename:package.json repo:${repo.owner.login}/${repo.name}`,
    ),
  });

  // TODO: Pagination
  for (const item of response.data.items) {
    const tree = item.path;

    /*
      1. Use graphql to fetch file contenst from this tree
    */
  }
}
