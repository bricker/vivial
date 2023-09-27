import { logEvent } from "@eave-fyi/eave-stdlib-ts/src/analytics.js";
import { FileChange } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
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

export class PullRequestCreator {
  private repoName: string;

  private repoOwner: string;

  private repoId: string;

  // expected to have the 'refs/heads/' prefix
  private baseBranchName: string;

  private octokit: Octokit;

  private ctx: LogContext;

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
   * branch off the head commit (should usually be PR merge commit)
   * https://docs.github.com/en/graphql/reference/mutations#createref
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
      eaveLogger.error(
        `Failed to create branch in ${this.repoOwner}/${this.repoName}`,
        this.ctx,
      );
      throw new Error("Failed to create branch");
    }
    return docsBranch;
  }

  /**
   * commit file changes
   * https://docs.github.com/en/graphql/reference/mutations#createcommitonbranch
   *
   * @param fileChanges - `contents` field of each `FileChange` object must be base64 encoded
   */
  private async createCommit(
    branch: Ref,
    message: string,
    fileChanges: Array<FileChange>,
  ): Promise<void> {
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
      fileChanges: {
        additions: fileChanges,
      },
    };
    const commitResp = await this.octokit.graphql<{
      createCommitOnBranch: Mutation["createCommitOnBranch"];
    }>(createCommitMutation, createCommitParameters);
    if (!commitResp.createCommitOnBranch?.commit?.oid) {
      eaveLogger.error(
        `Failed to create commit in ${this.repoOwner}/${this.repoName}`,
        this.ctx,
      );
      await this.deleteBranch(branch!.id);
      throw new Error("Failed to create commit");
    }
  }

  /**
   * open new PR against event.pull_request.base.ref (same base as PR that triggered this event)
   * https://docs.github.com/en/graphql/reference/mutations#createpullrequest
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
      eaveLogger.error(
        `Failed to create PR in ${this.repoOwner}/${this.repoName}`,
        this.ctx,
      );
      await this.deleteBranch(branch!.id);
      throw new Error("Failed to open PR");
    }
    return prResp.createPullRequest.pullRequest;
  }

  // https://docs.github.com/en/graphql/reference/mutations#deleteref
  private async deleteBranch(branchNodeId: string): Promise<void> {
    const query = await GraphQLUtil.loadQuery("deleteBranch");
    const params: {
      refNodeId: Scalars["ID"]["input"];
    } = {
      refNodeId: branchNodeId,
    };
    await this.octokit.graphql<{ resp: Mutation["deleteRef"] }>(query, params);
  }

  private ensureBranchPrefix(branchName: string): string {
    const githubBranchPrefix = "refs/heads/";
    if (branchName.startsWith(githubBranchPrefix)) {
      return branchName;
    }
    return `${githubBranchPrefix}${branchName}`;
  }

  /**
   * Open a new PR containing the input `fileChanges`, targeted at `baseBranchName`.
   * Input parameters used for PR creation details.
   * @returns the number of the created PR
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
    fileChanges: Array<FileChange>;
  }): Promise<PullRequest> {
    const branch = await this.createBranch(this.ensureBranchPrefix(branchName));
    await this.createCommit(branch, commitMessage, fileChanges);
    const pr = await this.openPullRequest(branch, prTitle, prBody);

    await logEvent(
      {
        event_name: "eave_github_pull_request_opened",
        event_description: "Eave GitHub app opened a PR",
      },
      this.ctx,
    );

    return pr;
  }
}
