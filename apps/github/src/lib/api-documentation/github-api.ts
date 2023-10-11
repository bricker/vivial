import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { JsonValue } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import {
  Blob,
  Query,
  Repository,
  Scalars,
  Tree,
  TreeEntry,
} from "@octokit/graphql-schema";
import { Octokit } from "octokit";
import path from "path";
import { GitHubOperationsContext } from "../../types.js";
import {
  assertIsBlob,
  assertIsRepository,
  assertIsTree,
  isBlob,
  isTree,
  loadQuery,
} from "../graphql-util.js";
import { EaveGithubRepoArg, ExternalGithubRepoArg } from "./args.js";

export class GithubAPIData {
  readonly logParams: { [key: string]: JsonValue };
  readonly expressRootDirs: string[];
  readonly externalGithubRepo: Repository;
  private readonly ctx: LogContext;
  private readonly octokit: Octokit;

  static async load({
    ctx,
    octokit,
    eaveGithubRepo,
  }: GitHubOperationsContext & EaveGithubRepoArg) {
    let externalGithubRepo;
    let expressRootDirs;

    {
      const query = await loadQuery("getRepo");
      const variables: {
        nodeId: Scalars["ID"]["input"];
      } = {
        nodeId: eaveGithubRepo.external_repo_id,
      };

      const response = await octokit.graphql<{ node: Query["node"] }>(
        query,
        variables,
      );

      assertIsRepository(response.node);
      externalGithubRepo = response.node;
    }

    {
      const query = `"\\"express\\":" in:file filename:package.json repo:${externalGithubRepo.owner.login}/${externalGithubRepo.name}`;
      const response = await octokit.rest.search.code({
        q: query,
      });

      expressRootDirs = response.data.items.map((i) => path.dirname(i.path));

      if (expressRootDirs.length === 0) {
        eaveLogger.warning(
          "No express API dir file found",
          { eave_github_repo: eaveGithubRepo, query },
          ctx,
        );
      }
    }

    return new GithubAPIData({
      ctx,
      octokit,
      externalGithubRepo,
      expressRootDirs,
    });
  }

  private constructor({
    ctx,
    octokit,
    externalGithubRepo,
    expressRootDirs,
  }: GitHubOperationsContext &
    ExternalGithubRepoArg & { expressRootDirs: string[] }) {
    this.ctx = ctx;
    this.octokit = octokit;
    this.externalGithubRepo = externalGithubRepo;
    this.expressRootDirs = expressRootDirs;

    this.logParams = {
      external_github_repo: {
        id: this.externalGithubRepo.id,
        nameWithOwner: this.externalGithubRepo.nameWithOwner,
      },
      express_root_dirs: this.expressRootDirs,
    };
  }

  async getGitTree({ treeRootDir }: { treeRootDir: string }): Promise<Tree> {
    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: this.externalGithubRepo.owner.login,
      repoName: this.externalGithubRepo.name,
      expression: `${
        this.externalGithubRepo.defaultBranchRef!.name
      }:${treeRootDir}`,
    };

    const response = await this.octokit.graphql<{
      repository: Query["repository"];
    }>(query, variables);

    assertIsRepository(response.repository);
    const repository = response.repository;

    assertIsTree(repository.object);
    const tree = repository.object;

    return tree;
  }

  async *recurseGitTree({
    treeRootDir,
  }: {
    treeRootDir: string;
  }): AsyncGenerator<TreeEntry> {
    const gitTree = await this.getGitTree({ treeRootDir });
    const blobEntries = gitTree.entries?.filter((e) => isBlob(e.object));
    const subTrees = gitTree.entries?.filter((e) => isTree(e.object));

    // BFS
    if (blobEntries) {
      for (const blobEntry of blobEntries) {
        // TODO: How to design this function to return a TreeEntry narrowed to `TreeEntry.object.__typename === "Blob"`, so the caller doesn't have to assert?
        yield blobEntry;
      }
    }

    if (subTrees) {
      for (const subTree of subTrees) {
        assertPresence(subTree.path);
        yield* this.recurseGitTree({ treeRootDir: subTree.path });
      }
    }
  }

  async getFileContent({
    filePath,
  }: {
    filePath: string;
  }): Promise<Blob | null> {
    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: this.externalGithubRepo.owner.login,
      repoName: this.externalGithubRepo.name,
      expression: `${
        this.externalGithubRepo.defaultBranchRef?.name || "main"
      }:${filePath}`,
    };

    const response = await this.octokit.graphql<{
      repository: Query["repository"];
    }>(query, variables);

    eaveLogger.debug(
      "getGitObject response",
      { variables, object_id: response.repository?.object?.id || null},
      { github_data: this.logParams },
      this.ctx,
    );

    assertIsRepository(response.repository);
    const repository = response.repository;

    if (!repository.object) {
      return null;
    }

    assertIsBlob(repository.object);
    return repository.object;
  }
}
