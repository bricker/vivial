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

  /**
   * Asynchronously loads the GitHub repository and Express root directories based on the provided context and repository arguments.
   *
   * @param ctx - The GitHub operations context.
   * @param octokit - The Octokit instance to interact with GitHub's API.
   * @param eaveGithubRepo - The Eave GitHub repository argument.
   *
   * @returns A new instance of GithubAPIData containing the context, Octokit instance, external GitHub repository, and Express root directories.
   *
   * @throws Will throw an error if no Express API directory file is found.
   */
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
          { core_api_data: { eave_github_repo: eaveGithubRepo }, query },
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

  /**
   * A private constructor that initializes the GitHubOperationsContext, ExternalGithubRepoArg, and expressRootDirs.
   * @param {Object} args - The arguments object.
   * @param {Object} args.ctx - The GitHubOperationsContext object.
   * @param {Object} args.octokit - The Octokit object.
   * @param {Object} args.externalGithubRepo - The ExternalGithubRepoArg object.
   * @param {string[]} args.expressRootDirs - The array of express root directories.
   */
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

  /**
   * Retrieves the Git tree for a specified root directory.
   *
   * @param {Object} params - The parameters for the function.
   * @param {string} params.treeRootDir - The root directory of the tree to retrieve.
   *
   * @returns {Promise<Tree>} A promise that resolves to the Git tree for the specified root directory.
   *
   * @throws {Error} If the response does not contain a valid repository or tree.
   */
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

  /**
   * An asynchronous generator function that performs a breadth-first search (BFS) on a Git tree.
   * It yields each blob entry in the tree and recursively explores sub-trees.
   *
   * @param {Object} params - The parameters for the function.
   * @param {string} params.treeRootDir - The root directory of the Git tree to be traversed.
   * @yields {TreeEntry} - Yields each blob entry in the Git tree.
   * @throws {AssertionError} - If the path of a sub-tree is not present.
   */
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

  /**
   * Retrieves the content of a file from a GitHub repository.
   *
   * @param {Object} params - The parameters for the function.
   * @param {string} params.filePath - The path of the file in the repository.
   *
   * @returns {Promise<Blob | null>} The content of the file as a Blob if the file exists, otherwise null.
   *
   * @throws {Error} If the response from the GitHub API does not contain a valid repository or Blob.
   */
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
