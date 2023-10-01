import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
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
import { Blob, FileAddition, FileChanges, Maybe, Query, Repository, Scalars, Tree, TreeEntry } from "@octokit/graphql-schema";
import assert, { AssertionError } from "assert";
import Express from "express";
import { appConfig } from "../config.js";
import { loadQuery } from "../lib/graphql-util.js";
import { createOctokitClient, getInstallationId } from "../lib/octokit-util.js";
import { PullRequestCreator } from "../lib/pull-request-creator.js";
import { GitHubOperationsContext } from "../types.js";
import { components } from "@octokit/openapi-types";
import { ProgrammingLanguage, getProgrammingLanguageByExtension, getProgrammingLanguageByFilePathOrName } from "@eave-fyi/eave-stdlib-ts/src/programming-langs/language-mapping.js";
import Parser from "tree-sitter";
import { ExpressAPI, ExpressParsingUtility } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { CodeFile } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/parsing-utility.js";
import path from "path";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import { assertPresence, underscoreify } from "@eave-fyi/eave-stdlib-ts/src/util.js";

type GithubApiCallerArgs = GitHubOperationsContext & { repo: Repository, parser: ExpressParsingUtility };

const IGNORE_DIRS = [
  "node_modules",
];

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
  }, ctx);

  const externalRepo = await getExternalRepo({ repo, octokit, ctx });

  const parser = new ExpressParsingUtility({ ctx });

  const fwdArgs = { repo: externalRepo, octokit, ctx, parser };

  const expressApiRootDirs = await getExpressAPIRootDirs({ repo: externalRepo, parser, octokit, ctx });

  if (expressApiRootDirs.length === 0) {
    await logEvent({
      event_name: "express_api_detection_no_apps_detected",
      event_description:
        "The API documentation feature is enabled for this repository, but no express apps were not detected.",
      eave_team: team,
      event_source: "github app",
      opaque_params: {
        repo,
      },
    }, ctx);

    eaveLogger.warning("No express apps found", repo, ctx);
    res.sendStatus(200);
    return;
  }

  const existingEaveDocs = await getExistingGithubDocuments({ repo, team, ctx });

  const results = await Promise.allSettled(expressApiRootDirs.map(async (rootDir) => {
    const apiInfo = await getExpressApiInfo({ rootDir, team, eaveRepo: repo, ...fwdArgs });
    assertPresence(apiInfo);
    assertPresence(apiInfo.rootFile);

    let eaveDoc = existingEaveDocs.find((d) => d.file_path === apiInfo.documentationFilePath);
    if (eaveDoc) {
      eaveDoc = await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { api_name: apiInfo.name, file_path: apiInfo.documentationFilePath, status: Status.PROCESSING } });
    } else {
      eaveDoc = await createPlaceholderGithubDocument({ apiInfo, repo, team, ctx });
    }

    const endpoints = await getExpressAPIEndpoints({ apiRootFilePath: apiInfo.rootFile.path, ...fwdArgs });
    if (!endpoints || endpoints.length === 0) {
      await logEvent({
        event_name: "express_api_detection_no_endpoints",
        event_description:
          "An express API was detected, but no endpoints were found.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);

      eaveLogger.warning("No express API endpoints found", { rootDir, expressApiRootFile: apiInfo.rootFile.path, apiName: apiInfo.name }, repo, externalRepo, ctx);
      await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { status: Status.FAILED } });
      return Promise.reject();
    }

    apiInfo.endpoints = endpoints;

    const newDocumentContents = await parser.generateExpressAPIDoc({ api: apiInfo, ctx});
    if (!newDocumentContents) {
      await logEvent({
        event_name: "express_api_documentation_not_generated",
        event_description:
          "Documentation for an express API was not generated, so the resulting document was empty. No pull request will be opened.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);
      eaveLogger.warning("Empty express API documentation.", { rootDir, expressApiRootFile: apiInfo.rootFile.path, apiName: apiInfo.name }, repo, externalRepo, ctx);

      await updateGithubDocument({ team, ctx, document: eaveDoc, newValues: { status: Status.FAILED } });
      return Promise.reject();
    } else {
      await logEvent({
        event_name: "express_api_documentation_generated",
        event_description:
          "Documentation for an express API was successfully generated.",
        eave_team: team,
        event_source: "github app",
        opaque_params: {
          repo,
          externalRepo,
          rootDir,
          expressApiRootFile: apiInfo.rootFile.path,
          language: apiInfo.rootFile.language,
          apiName: apiInfo.name,
        },
      }, ctx);
      apiInfo.documentation = newDocumentContents;
      return apiInfo;
    }
  }));

  const documents = results.filter((r) => r.status === "fulfilled").map((r) => (<PromiseFulfilledResult<ExpressAPI>>r).value);

  const fileAdditions: FileAddition[] = documents.map((d) => {
    assertPresence(d.documentation);
    assertPresence(d.documentation);
    return {
      path: d.documentationFilePath,
      contents: Buffer.from(d.documentation).toString("base64"),
    }
  });

  const prCreator = new PullRequestCreator({
    repoName: externalRepo.name,
    repoOwner: externalRepo.owner.login,
    repoId: externalRepo.id,
    baseBranchName: externalRepo.defaultBranchRef?.name || "main", // The only reason `defaultBranchRef` would be undefined is if it wasn't specified in the query fields. But defaulting to "main" is easier than handling the runtime error and will work for most cases.
    octokit,
    ctx,
  });

  const pullRequest = await prCreator.createPullRequest({
    branchName: "refs/heads/eave/auto-docs/api",
    commitMessage: "docs: automated update",
    prTitle: "docs: Eave API documentation update",
    prBody: "Your new API docs based on recent changes to your code",
    fileChanges: {
      additions: fileAdditions,
    },
  });

  for (const document of documents) {
    const eaveDoc = existingEaveDocs.find((d) => d.file_path === document.documentationFilePath);
    assertPresence(eaveDoc);
    await updateGithubDocument({
      document: eaveDoc,
      team,
      ctx,
      newValues: {
        pull_request_number: pullRequest.number,
        status: Status.PR_OPENED,
      },
    });
  }
}

async function getExpressApiInfo({ rootDir, team, eaveRepo, repo, octokit, parser, ctx }: GithubApiCallerArgs & { team: Team, eaveRepo: GithubRepo, rootDir: string }): Promise<ExpressAPI | null> {
  const fwdArgs = { repo, octokit, parser, ctx };

  const api = new ExpressAPI({
    rootDir,
  });

  const expressApiRootFile = await getExpressAPIRootFile({ apiRootDir: rootDir, ...fwdArgs });
  if (!expressApiRootFile) {
    // We thought this dir contained an Express app, but couldn't find a file that initialized the express server.
    await logEvent({
      event_name: "express_api_detection_false_positive",
      event_description:
        "An express API was detected, but no root file was found.",
      eave_team: team,
      event_source: "github app",
      opaque_params: {
        repo,
        eaveRepo,
        rootDir,
      },
    }, ctx);

    eaveLogger.warning("No express API root file found", { rootDir }, repo, eaveRepo, ctx);
    return null;
  }
  assert(expressApiRootFile.path, "unexpected missing path property");

  api.rootFile = expressApiRootFile;

  const apiName = await parser.guessExpressAPIName({ apiDir: rootDir });
  api.name = apiName;
  return api;
}

/**
 * Given the root file for an Express API, this function attempts to identify
 * each API endpoint in the file. It then builds the code for each endpoint.
 */
async function getExpressAPIEndpoints({
  apiRootFilePath,
  parser,
  repo, octokit, ctx
}: GithubApiCallerArgs & {
  apiRootFilePath: string;
}): Promise<Array<string> | null> {
  const fwdArgs = { repo, octokit, ctx, parser };

  const apiRootFile = await getFileContent({ filePath: apiRootFilePath, ...fwdArgs });
  assert(apiRootFile, "unexpected missing file object");

  const tree = parser.parseCode({ file: apiRootFile });
  const calls = tree.rootNode.descendantsOfType("call_expression");
  const requires = await buildLocalRequires({ tree, file: apiRootFile, ...fwdArgs });
  const imports = await buildLocalImports({ tree, file: apiRootFile, ...fwdArgs });
  const declarations = parser.getDeclarationMap({ tree });
  const { app = "", router = "" } = await parser.getExpressAppIdentifiers({
    tree,
  });
  const apiEndpoints: Array<string> = [];

  let baseCode = `import express from 'express';\nconst ${app} = express();\n`;
  if (router) {
    baseCode += `const ${router} = express.Router();\n`;
  }

  for (const call of calls) {
    const isMiddleWareCall = call.text.startsWith(`${app}.use`);
    if (isMiddleWareCall) {
      baseCode += `${call.text}\n`;
    }

    const isRouteCall = await parser.isExpressRouteCall({
      node: call,
      app,
      router,
    });
    if (isRouteCall) {
      let endpointCode = `${baseCode}\n${call.text}\n\n`;
      const nestedIdentifiers = parser.getUniqueIdentifiers({
        rootNode: call,
        exclusions: [app, router],
      });
      for (const identifier of nestedIdentifiers) {
        const importCode = imports.get(identifier);
        if (importCode) {
          endpointCode += importCode;
          continue;
        }
        const requireCode = requires.get(identifier);
        if (requireCode) {
          endpointCode += requireCode;
          continue;
        }
        const declarationCode = declarations.get(identifier)?.text;
        if (declarationCode) {
          endpointCode += `${declarationCode}\n\n`;
        }
      }
      apiEndpoints.push(endpointCode);
    }
  }

  return apiEndpoints;
}

/**
 * Given a top-level declaration identifier, this function recursively builds
 * up all of the local source code for that declaration.
 */
async function buildExpressCode({
  identifier,
  filePath,
  accumulator = "",
  repo,
  octokit,
  ctx,
  parser,
}: GithubApiCallerArgs & {
  identifier: string;
  filePath: string;
  accumulator?: string;
}): Promise<string | null> {
  const fwdArgs = { repo, octokit, ctx, parser };
  assert(filePath, "unexpected missing filePath");
  assert(identifier, "unexpected missing identifier");

  const file = await getFileContent({ filePath, ...fwdArgs });
  assert(file, "unexpected missing file object");

  const tree = parser.parseCode({ file });
  const declarations = parser.getDeclarationMap({ tree });
  const declaration = declarations.get(identifier);

  // Case 2: The given identifier is declared in the given file.
  if (declaration) {
    accumulator += `${declaration.text}\n\n`;
    const importPaths = parser.getLocalImportPaths({ tree, file });
    const requirePaths = parser.getLocalRequirePaths({ tree, file });
    const innerIdentifiers = parser.getUniqueIdentifiers({
      rootNode: declaration,
      exclusions: [identifier],
    });

    for (const innerIdentifier of innerIdentifiers) {
      const innerDeclaration = declarations.get(innerIdentifier);
      const isRequire = innerDeclaration?.text.match(/require\(["|'][^"|']["|']\)/);
      if (innerDeclaration && !isRequire) {
        accumulator += `${innerDeclaration.text}\n\n`;
        continue;
      }
      const importPath = importPaths.get(innerIdentifier);
      if (importPath) {
        const c = await buildExpressCode({
          identifier: innerIdentifier,
          filePath: importPath,
          accumulator,
          ...fwdArgs,
        });
        if (c) {
          accumulator = c;
        }
        continue;
      }
      const requirePath = requirePaths.get(innerIdentifier);
      if (requirePath) {
        const c = await buildExpressCode({
          identifier: innerIdentifier,
          filePath: requirePath,
          accumulator,
          ...fwdArgs,
        });
        if (c) {
          accumulator = c;
        }
      }
    }
    return accumulator;
  }

  // FIXME: This is broken (filePath being passed into recursive func
  // // Case 3: The declaration we're looking for wasn't found -- check for default export.
  // const exportNodes = tree.rootNode.descendantsOfType("export_statement");
  // for (const exportNode of exportNodes) {
  //   const children = parser.getNodeChildMap({ node: exportNode });
  //   if (children.has("default")) {
  //     const defaultIdentifier = children.get("identifier")?.text;
  //     if (defaultIdentifier) {
  //       const c = await buildExpressCode({
  //         identifier: defaultIdentifier,
  //         filePath,
  //         accumulator,
  //         ...fwdArgs,
  //       });
  //       if (c) {
  //         accumulator = c;
  //         accumulator = c.replaceAll(defaultIdentifier, identifier);
  //       }
  //     }
  //   }
  // }

  return accumulator;
}

/**
 * Given a tree, builds the local source code for the top-level imports found
 * in the tree. Returns the code in a map for convenient lookup.
 */
async function buildLocalImports({
  tree,
  file,
  repo, octokit, ctx, parser
}: GithubApiCallerArgs & {
  tree: Parser.Tree;
  file: CodeFile;
}): Promise<Map<string, string>> {
  const fwdArgs = { repo, octokit, ctx, parser };
  const importPaths = parser.getLocalImportPaths({
    tree,
    file,
  });
  const imports = new Map();
  for (const [identifier, importPath] of importPaths) {
    const importCode = await buildExpressCode({
      identifier,
      filePath: importPath,
      ...fwdArgs,
    });
    imports.set(identifier, importCode);
  }
  return imports;
}

/**
 * Given a tree, builds the local source code for the top-level required modules
 * found the tree. Returns the code in a map for convenient lookup.
 */
async function buildLocalRequires({
  tree,
  file,
  repo, octokit, ctx, parser,
}: GithubApiCallerArgs & {
  tree: Parser.Tree;
  file: CodeFile;
}): Promise<Map<string, string>> {
  const fwdArgs = { repo, octokit, parser, ctx };
  const requirePaths = parser.getLocalRequirePaths({
    tree,
    file,
  });
  const requires = new Map();
  for (const [identifier, requirePath] of requirePaths) {
    const requireCode = await buildExpressCode({
      identifier,
      filePath: requirePath,
      ...fwdArgs,
    });
    requires.set(identifier, requireCode);
  }
  return requires;
}

async function getFileContent({ filePath, repo, octokit, ctx, parser }: GithubApiCallerArgs & { filePath: string }): Promise<CodeFile | null> {
  const file = new CodeFile({ path: filePath });
  const query = await loadQuery("getGitObject");
  const variables: {
    repoOwner: Scalars["String"]["input"];
    repoName: Scalars["String"]["input"];
    expression: Scalars["String"]["input"];
  } = {
    repoOwner: repo.owner.login,
    repoName: repo.name,
    expression: `${repo.defaultBranchRef?.name}:${file.path}`,
  };

  const response = await octokit.graphql<{ repository: Query["repository"] }>(
    query,
    variables,
  );

  eaveLogger.debug("getGitObject response", { query, variables, response }, ctx);

  let repository = <Repository>response.repository;

  if (repository.object === null && file.language === ProgrammingLanguage.javascript) {
    // either the file doesn't exist, or this is a javascript import and the source file is typescript.
    const tsPath = parser.changeFileExtension({ filePathOrName: filePath, to: ".ts" });
    variables.expression = `${repo.defaultBranchRef?.name}:${tsPath}`;
    const tsresponse = await octokit.graphql<{ repository: Query["repository"] }>(
      query,
      variables,
    );
    eaveLogger.debug("getGitObject response (ts try)", { query, variables, response: tsresponse }, ctx);
    repository = <Repository>tsresponse.repository;
  }

  assertIsBlob(repository.object);
  const code = repository.object.text;

  if (!code) {
    return null;
  }

  file.contents = code;
  return file;
}
