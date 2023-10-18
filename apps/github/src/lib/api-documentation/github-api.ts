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
  readonly externalRepoId: string;
  private readonly ctx: LogContext;
  private readonly octokit: Octokit;

  private __memo__latestCommitOnDefaultBranch?: Commit | null;
  private __memo__expressRootDirs?: string[];
  private __memo__externalGithubRepo?: Repository;

  constructor({
    ctx,
    octokit,
    externalRepoId,
  }: GitHubOperationsContext & { externalRepoId: string; }) {
    this.ctx = ctx;
    this.octokit = octokit;
    this.externalRepoId = externalRepoId;

    this.logParams = {};
  }

  async getExternalGithubRepo(): Promise<Repository> {
    if (this.__memo__externalGithubRepo !== undefined) {
      return this.__memo__externalGithubRepo;
    }

    const query = await loadQuery("getRepo");
    const variables: {
      nodeId: Scalars["ID"]["input"];
    } = {
      nodeId: this.externalRepoId,
    };

    const response = await this.octokit.graphql<{ node: Query["node"] }>(
      query,
      variables,
    );

    const externalGithubRepo = response.node;
    assertIsRepository(externalGithubRepo);

    this.logParams["external_github_repo"] = {
      id: externalGithubRepo.id,
      nameWithOwner: externalGithubRepo.nameWithOwner,
    };
    this.__memo__externalGithubRepo = externalGithubRepo;
    return this.__memo__externalGithubRepo;
  }

  async getExpressRootDirs(): Promise<string[]> {
    if (this.__memo__expressRootDirs !== undefined) {
      return this.__memo__expressRootDirs;
    }

    const externalGithubRepo = await this.getExternalGithubRepo();
    const query = `"\\"express\\":" in:file filename:package.json repo:${externalGithubRepo.owner.login}/${externalGithubRepo.name}`;
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
    this.__memo__expressRootDirs = expressRootDirs;
    return expressRootDirs;
  }

  async getLatestCommitOnDefaultBranch(): Promise<Commit | null> {
    if (this.__memo__latestCommitOnDefaultBranch !== undefined) {
      return this.__memo__latestCommitOnDefaultBranch;
    }

    const externalGithubRepo = await this.getExternalGithubRepo();
    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: externalGithubRepo.owner.login,
      repoName: externalGithubRepo.name,
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

    this.__memo__latestCommitOnDefaultBranch = latestCommitOnDefaultBranch;
    return latestCommitOnDefaultBranch;
  }

  async getGitTree({ treeRootDir }: { treeRootDir: string }): Promise<Tree> {
    const externalGithubRepo = await this.getExternalGithubRepo();
    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: externalGithubRepo.owner.login,
      repoName: externalGithubRepo.name,
      expression: `${
        externalGithubRepo.defaultBranchRef!.name
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
    const externalGithubRepo = await this.getExternalGithubRepo();
    const query = await loadQuery("getGitObject");
    const variables: {
      repoOwner: Scalars["String"]["input"];
      repoName: Scalars["String"]["input"];
      expression: Scalars["String"]["input"];
    } = {
      repoOwner: externalGithubRepo.owner.login,
      repoName: externalGithubRepo.name,
      expression: `${
        externalGithubRepo.defaultBranchRef?.name || "main"
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
