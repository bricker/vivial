import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import {
  eaveLogger,
  LogContext,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import {
  CommitMessage,
  CommittableBranch,
  FileChanges,
  Mutation,
  PullRequest,
  Query,
  Ref,
  Scalars,
} from "@octokit/graphql-schema";
import { Octokit } from "octokit";
import * as GraphQLUtil from "../lib/graphql-util.js";
import { assertPresence } from "@eave-fyi/eave-stdlib-ts/src/util.js";

export class PullRequestCreator {
  private repoName: string;

  private repoOwner: string;

  private repoId: string;

  // expected to have the 'refs/heads/' prefix
  private baseBranchName: string;

  private octokit: Octokit;

  private ctx: LogContext;

  /**
   * Constructs a new instance of the class.
   *
   * @param {Object} args - The arguments for the constructor.
   * @param {string} args.repoName - The name of the repository.
   * @param {string} args.repoOwner - The owner of the repository.
   * @param {string} args.repoId - The ID of the repository.
   * @param {string} args.baseBranchName - The name of the base branch in the repository.
   * @param {Octokit} args.octokit - The Octokit instance to interact with GitHub.
   * @param {LogContext} args.ctx - The logging context.
   */
  constructor({
    repoName,
    repoOwner,
    repoId,
    baseBranchName,
    octokit,
    ctx,
  }: {
    repoName: string;
    repoOwner: string;
    repoId: string;
    baseBranchName: string;
    octokit: Octokit;
    ctx: LogContext;
  }) {
    this.repoName = repoName;
    this.repoOwner = repoOwner;
    this.octokit = octokit;
    this.ctx = ctx;
    this.repoId = repoId;
    this.baseBranchName = this.ensureBranchPrefix(baseBranchName);
  }

  /**
   * Retrieves a specific branch from a repository using the provided branch name.
   * Utilizes GraphQL to load the 'getRef' query and execute it with the necessary parameters.
   * If the branch does not exist, it returns null.
   *
   * @param branchName - The name of the branch to retrieve.
   * @returns A Promise that resolves to the branch reference or null if the branch does not exist.
   */
  private async getBranch(branchName: string): Promise<Ref | null> {
    const getBranchQuery = await GraphQLUtil.loadQuery("getRef");
    const getBranchParameters: {
      repoName: Scalars["String"]["input"];
      repoOwner: Scalars["String"]["input"];
      refName: Scalars["String"]["input"];
    } = {
      repoName: this.repoName,
      repoOwner: this.repoOwner,
      refName: branchName,
    };

    const branchResp = await this.octokit.graphql<{
      repository: Query["repository"];
    }>(getBranchQuery, getBranchParameters);

    GraphQLUtil.assertIsRepository(branchResp.repository);
    const ref = branchResp.repository.ref;
    return ref || null;
  }

  /**
   * Asynchronously creates a new branch in the repository, branching off the head commit (should usually be PR merge commit).
   *
   * @param branchName - The name of the branch to be created.
   *
   * @returns A promise that resolves to the created branch reference.
   *
   * @throws Will throw an error if the base branch's head commit cannot be fetched or if the branch creation fails.
   *
   * @see {@link https://docs.github.com/en/graphql/reference/mutations#createref}
   *
   * @private
   */
  private async createBranch(branchName: string): Promise<Ref> {
    // get base branch head commit
    const getHeadCommitQuery = await GraphQLUtil.loadQuery(
      "getBranchHeadCommit",
    );
    const getHeadCommitParams: {
      repoName: Scalars["String"]["input"];
      repoOwner: Scalars["String"]["input"];
      branchName: Scalars["String"]["input"];
    } = {
      repoName: this.repoName,
      repoOwner: this.repoOwner,
      branchName: this.baseBranchName,
    };
    const headResp = await this.octokit.graphql<{
      repository: Query["repository"];
    }>(getHeadCommitQuery, getHeadCommitParams);
    const commitHead = headResp.repository?.ref?.target;
    if (!commitHead) {
      eaveLogger.error(
        `Failed to fetch ${this.baseBranchName} head commit from ${this.repoOwner}/${this.repoName}`,
        this.ctx,
      );
      throw new Error("Failed to create branch");
    }

    const createBranchMutation = await GraphQLUtil.loadQuery("createBranch");
    const createBranchParameters: {
      repoId: Scalars["ID"]["input"];
      branchName: Scalars["String"]["input"];
      commitHeadId: Scalars["GitObjectID"]["input"];
    } = {
      commitHeadId: commitHead.oid,
      branchName,
      repoId: this.repoId,
    };

    const branchResp = await this.octokit.graphql<{
      createRef: Mutation["createRef"];
    }>(createBranchMutation, createBranchParameters);
    const docsBranch = branchResp.createRef?.ref;
    if (!docsBranch) {
      throw new Error("Failed to create branch");
    }
    return docsBranch;
  }

  /**
   * Asynchronously creates a commit on a specified branch with a given message and file changes.
   * If there are no file changes (additions or deletions), the function will return without creating a commit.
   * https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch
   *
   * @param branch - The branch on which the commit is to be created.
   * @param message - The commit message.
   * @param fileChanges - The changes to be committed, including file additions and deletions. `contents` field of each `FileChange` object must be base64 encoded.
   * @returns A promise that resolves to void when the commit is successfully created.
   *
   * @throws Will throw an error if the commit creation fails.
   */
  private async createCommit(
    branch: Ref,
    message: string,
    fileChanges: FileChanges,
  ): Promise<void> {
    if (!fileChanges.additions?.length && !fileChanges.deletions?.length) {
      return;
    }

    const createCommitMutation = await GraphQLUtil.loadQuery(
      "createCommitOnBranch",
    );
    const createCommitParameters: {
      branch: CommittableBranch;
      headOid: Scalars["GitObjectID"];
      message: CommitMessage;
      fileChanges: FileChanges;
    } = {
      branch: {
        branchName: branch.name,
        repositoryNameWithOwner: `${this.repoOwner}/${this.repoName}`,
      },
      headOid: branch.target!.oid,
      message: { headline: message },
      fileChanges,
    };
    const commitResp = await this.octokit.graphql<{
      createCommitOnBranch: Mutation["createCommitOnBranch"];
    }>(createCommitMutation, createCommitParameters);

    eaveLogger.debug("createCommitOnBranch response", {
      variables: {
        branch: createCommitParameters.branch,
        headOid: createCommitParameters.headOid,
        message: createCommitParameters.message,
        fileChangesLength: createCommitParameters.fileChanges.additions?.length,
      },
      response: {
        commit_oid: commitResp.createCommitOnBranch?.commit?.oid,
      },
    });

    if (!commitResp.createCommitOnBranch?.commit?.oid) {
      throw new Error("Failed to create commit");
    }
  }

  /**
   * Opens a new pull request on the specified branch, against event.pull_request.base.ref (same base as PR that triggered this event).
   * https://docs.github.com/en/graphql/reference/mutations#createpullrequest
   *
   * @param branch - The branch where the pull request will be opened.
   * @param prTitle - The title of the pull request.
   * @param prBody - The body content of the pull request.
   * @returns A promise that resolves to the newly created pull request.
   * @throws Will throw an error if the pull request creation fails.
   */
  private async openPullRequest(
    branch: Ref,
    prTitle: string,
    prBody: string,
  ): Promise<PullRequest> {
    const createPrMutation = await GraphQLUtil.loadQuery("createPullRequest");
    const createPrParameters: {
      baseRefName: Scalars["String"]["input"];
      body: Scalars["String"]["input"];
      headRefName: Scalars["String"]["input"];
      repoId: Scalars["ID"]["input"];
      title: Scalars["String"]["input"];
    } = {
      repoId: this.repoId,
      baseRefName: this.baseBranchName,
      headRefName: branch!.name,
      title: prTitle,
      body: prBody,
    };
    const prResp = await this.octokit.graphql<{
      createPullRequest: Mutation["createPullRequest"];
    }>(createPrMutation, createPrParameters);
    if (!prResp.createPullRequest?.pullRequest?.number) {
      throw new Error("Failed to open PR");
    }
    return prResp.createPullRequest.pullRequest;
  }

  /**
   * Deletes a specific branch using its node ID.
   *
   * @param branchNodeId - The unique identifier of the branch to be deleted.
   * @returns A promise that resolves when the branch deletion is complete.
   *
   * @remarks
   * This method uses the `deleteBranch` query from `GraphQLUtil` and the `deleteRef` mutation from the Octokit GraphQL API.
   * The `branchNodeId` is used as the `refNodeId` parameter in the GraphQL query.
   *
   * @see
   * {@link https://docs.github.com/en/graphql/reference/mutations#deleteref | GitHub GraphQL API Documentation}
   */
  private async deleteBranch(branchNodeId: string): Promise<void> {
    const query = await GraphQLUtil.loadQuery("deleteBranch");
    const params: {
      refNodeId: Scalars["ID"]["input"];
    } = {
      refNodeId: branchNodeId,
    };
    await this.octokit.graphql<{ resp: Mutation["deleteRef"] }>(query, params);
  }

  /**
   * Ensures the provided branch name starts with the standard GitHub branch prefix ("refs/heads/").
   * If the branch name already starts with the prefix, it is returned as is.
   * Otherwise, the prefix is prepended to the branch name and the resulting string is returned.
   *
   * @param branchName - The name of the branch to check and possibly prefix.
   * @returns The branch name, prefixed with "refs/heads/" if it was not already.
   */
  private ensureBranchPrefix(branchName: string): string {
    const githubBranchPrefix = "refs/heads/";
    if (branchName.startsWith(githubBranchPrefix)) {
      return branchName;
    }
    return `${githubBranchPrefix}${branchName}`;
  }

  /**
   * Asynchronously creates a pull request on a given branch with specified changes.
   * If the branch does not exist, it will be created.
   * If a pull request already exists, new commits will be added to it.
   *
   * @param {Object} params - Parameters for creating a pull request.
   * @param {string} params.branchName - The name of the branch.
   * @param {string} params.commitMessage - The commit message.
   * @param {string} params.prTitle - The title of the pull request.
   * @param {string} params.prBody - The body text of the pull request.
   * @param {FileChanges} params.fileChanges - The changes to be committed.
   *
   * @returns {Promise<PullRequest | null>} A promise that resolves to the created pull request, or null if the pull request could not be created.
   *
   * @throws Will throw an error if the pull request creation fails.
   */
  public async createPullRequest({
    branchName,
    commitMessage,
    prTitle,
    prBody,
    fileChanges,
  }: {
    branchName: string;
    commitMessage: string;
    prTitle: string;
    prBody: string;
    fileChanges: FileChanges;
  }): Promise<PullRequest> {
    const fqBranchName = this.ensureBranchPrefix(branchName);
    let branch = await this.getBranch(fqBranchName);
    let createdNewBranch: boolean;

    if (branch) {
      createdNewBranch = false;
      await logEvent(
        {
          event_name: "eave_pushed_to_existing_branch",
          event_description:
            "Eave pushed a commit to a branch that already existed. This is normal.",
          opaque_params: {
            branch: {
              id: branch.id,
              name: branch.name,
            },
          },
        },
        this.ctx,
      );
    } else {
      branch = await this.createBranch(fqBranchName);
      createdNewBranch = true;

      await logEvent(
        {
          event_name: "eave_created_branch",
          event_description: "Eave created a new branch and pushed a commit.",
          opaque_params: {
            branch: {
              id: branch.id,
              name: branch.name,
            },
          },
        },
        this.ctx,
      );
    }

    await this.createCommit(branch, commitMessage, fileChanges);

    let pr: PullRequest;

    // fwiw, this should always be empty for a branch that was just created, so this line will implicitly skip to the `openPullRequest` block.
    // As of writing this, the query that gets this data only fetches the 1 most recently created open pull request. The sorting/filtering here is so that if the query is changed, this logic still works as expected.
    assertPresence(branch.associatedPullRequests, 'associatedPullRequests unexpectedly empty');

    const mostRecentExistingPr = branch.associatedPullRequests.nodes
      ?.filter((p) => p?.state === "OPEN")
      .sort(sortPRsByDescendingCreatedAt)
      .at(-1);
    if (mostRecentExistingPr) {
      pr = mostRecentExistingPr;

      await logEvent(
        {
          event_name: "eave_github_pull_request_appended",
          event_description:
            "Eave GitHub app added new commits to an existing PR",
          opaque_params: {
            branch: {
              id: branch.id,
              name: branch.name,
            },
            pull_request: {
              number: pr.number,
              updated_at: pr.updatedAt,
              created_at: pr.createdAt,
            },
          },
        },
        this.ctx,
      );
    } else {
      try {
        pr = await this.openPullRequest(branch, prTitle, prBody);

        await logEvent(
          {
            event_name: "eave_github_pull_request_opened",
            event_description: "Eave GitHub app opened a PR",
            opaque_params: {
              branch: {
                id: branch.id,
                name: branch.name,
              },
              pull_request: {
                number: pr.number,
                updated_at: pr.updatedAt,
                created_at: pr.createdAt,
              },
            },
          },
          this.ctx,
        );
      } catch (e: any) {
        eaveLogger.error(
          `Failed to create PR`,
          { repo_owner: this.repoOwner, repo_name: this.repoName },
          this.ctx,
        );

        // dont delete existing branches
        if (createdNewBranch) {
          await this.deleteBranch(branch!.id);

          await logEvent(
            {
              event_name: "github_orphan_branch_deleted",
              event_description:
                "A branch was created, but the attempt to open a pull request failed, so we deleted the branch to prevent an orphaned branch.",
              opaque_params: {
                branch: {
                  id: branch.id,
                  name: branch.name,
                },
              },
            },
            this.ctx,
          );
        }

        // re-raise
        throw e;
      }
    }

    return pr;
  }
}

function sortPRsByDescendingCreatedAt(
  a: PullRequest | null,
  b: PullRequest | null,
): number {
  return Date.parse(a!.createdAt) - Date.parse(b!.createdAt);
}
