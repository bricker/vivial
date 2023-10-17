import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { JsonValue } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";
import {
  Blob,
  Commit,
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
  isCommit,
  isTree,
  loadQuery,
} from "../graphql-util.js";
import { EaveGithubRepoArg, ExternalGithubRepoArg } from "./args.js";

export class GithubAPIData {
  readonly logParams: { [key: string]: JsonValue };
  readonly externalGithubRepo: Repository;
  private readonly ctx: LogContext;
  private readonly octokit: Octokit;

  private __memo__latestCommitOnDefaultBranch__?: Commit | null;
  private __memo__expressRootDirs__?: string[];

  static async load({
    ctx,
    octokit,
    eaveGithubRepo,
  }: GitHubOperationsContext & EaveGithubRepoArg) {
    let externalGithubRepo;

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

    return new GithubAPIData({
      ctx,
      octokit,
      externalGithubRepo,
    });
  }

  private constructor({
    ctx,
    octokit,
    externalGithubRepo,
  }: GitHubOperationsContext & ExternalGithubRepoArg) {
    this.ctx = ctx;
    this.octokit = octokit;
    this.externalGithubRepo = externalGithubRepo;

    this.logParams = {
      external_github_repo: {
        id: this.externalGithubRepo.id,
        nameWithOwner: this.externalGithubRepo.nameWithOwner,
      },
    };
  }

  async getExpressRootDirs(): Promise<string[]> {
    if (this.__memo__expressRootDirs__ !== undefined) {
      return this.__memo__expressRootDirs__;
    }

    const query = `"\\"express\\":" in:file filename:package.json repo:${this.externalGithubRepo.owner.login}/${this.externalGithubRepo.name}`;
    const response = await this.octokit.rest.search.code({
      q: query,
    });

    const expressRootDirs = response.data.items.map((i) => path.dirname(i.path));

    if (expressRootDirs.length === 0) {
      eaveLogger.warning(
        "No express API dir file found",
        this.logParams,
        this.ctx,
      );
    }

    this.logParams["express_root_dirs"] = expressRootDirs;
    this.__memo__expressRootDirs__ = expressRootDirs;
    return expressRootDirs;
  }

  async getLatestCommitOnDefaultBranch(): Promise<Commit | null> {
    if (this.__memo__latestCommitOnDefaultBranch__ !== undefined) {
      return this.__memo__latestCommitOnDefaultBranch__;
    }

    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: this.externalGithubRepo.owner.login,
      repoName: this.externalGithubRepo.name,
      expression: "HEAD", // default branch by default
    };

    const response = await this.octokit.graphql<{ repository: Query["repository"] }>(
      query,
      variables,
    );

    assertIsRepository(response.repository);
    if (!isCommit(response.repository.object)) {
      return null;
    }

    let latestCommitOnDefaultBranch: Commit | null;
    if (isCommit(response.repository.object)) {
      latestCommitOnDefaultBranch = response.repository.object;
    } else {
      latestCommitOnDefaultBranch = null;
    }

    this.__memo__latestCommitOnDefaultBranch__ = latestCommitOnDefaultBranch;
    return latestCommitOnDefaultBranch;
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
      { variables, object_id: response.repository?.object?.id || null },
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
