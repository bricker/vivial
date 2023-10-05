import {
  DocumentType,
  GithubDocument,
  GithubDocumentValuesInput,
  Status,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import {
  CreateGithubDocumentOperation,
  GetGithubDocumentsOperation,
  UpdateGithubDocumentOperation,
} from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-documents.js";
import { GetGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { GetTeamOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js";
import { GithubRepoInput } from "@eave-fyi/eave-stdlib-ts/src/github-api/models.js";
import {
  LogContext,
  eaveLogger,
} from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import assert from "assert";
import { appConfig } from "../../config.js";
import { EaveGithubRepoArg } from "./args.js";

type GithubDocumentTable = { [key: string]: GithubDocument };

export class CoreAPIData {
  readonly team: Team;
  readonly eaveGithubRepo: GithubRepo;
  private readonly ctx: LogContext;
  readonly eaveGithubDocuments: GithubDocumentTable;

  static async load({
    ctx,
    teamId,
    eaveGithubRepoInput,
  }: CtxArg & { teamId: string; eaveGithubRepoInput: GithubRepoInput }) {
    let team: Team;
    let eaveGithubRepo: GithubRepo;
    const existingGithubDocuments: GithubDocumentTable = {};

    {
      const response = await GetTeamOperation.perform({
        origin: appConfig.eaveOrigin,
        teamId,
        ctx,
      });
      team = response.team;
    }

    {
      const response = await GetGithubReposOperation.perform({
        origin: appConfig.eaveOrigin,
        teamId: team.id,
        input: {
          repos: [eaveGithubRepoInput],
        },
        ctx,
      });

      if (response.repos.length > 1) {
        eaveLogger.warning(
          `Unexpected multiple repos for id ${eaveGithubRepoInput.external_repo_id}`,
          ctx,
        );
      }

      const r = response.repos[0];
      assert(
        r,
        `No repo found in Eave for ID ${eaveGithubRepoInput.external_repo_id}`,
      );
      eaveGithubRepo = r;
    }

    {
      const response = await GetGithubDocumentsOperation.perform({
        input: {
          query_params: {
            github_repo_id: eaveGithubRepo.id,
            type: DocumentType.API_DOCUMENT,
          },
        },
        origin: appConfig.eaveOrigin,
        teamId: team.id,
        ctx,
      });

      response.documents.forEach((doc) => {
        if (doc.file_path) {
          const key = githubDocumentKey({
            filePath: doc.file_path,
            externalRepoId: eaveGithubRepo.external_repo_id,
          });
          existingGithubDocuments[key] = doc;
        }
      });
    }

    return new CoreAPIData({
      team,
      ctx,
      eaveGithubRepo,
      existingGithubDocuments,
    });
  }

  private constructor({
    team,
    ctx,
    eaveGithubRepo,
    existingGithubDocuments,
  }: CtxArg &
    EaveGithubRepoArg & {
      team: Team;
      existingGithubDocuments: GithubDocumentTable;
    }) {
    this.ctx = ctx;
    this.team = team;
    this.eaveGithubRepo = eaveGithubRepo;
    this.eaveGithubDocuments = existingGithubDocuments;
  }

  async createPlaceholderGithubDocument({
    apiName,
    documentationFilePath,
  }: {
    apiName: string;
    documentationFilePath: string;
  }): Promise<GithubDocument> {
    const response = await CreateGithubDocumentOperation.perform({
      origin: appConfig.eaveOrigin,
      ctx: this.ctx,
      teamId: this.team.id,
      input: {
        repo: {
          id: this.eaveGithubRepo.id,
        },
        document: {
          type: DocumentType.API_DOCUMENT,
          status: Status.PROCESSING,
          api_name: apiName,
          file_path: documentationFilePath,
          pull_request_number: null,
        },
      },
    });

    this.setGithubDocument({ document: response.document });
    return response.document;
  }

  async updateGithubDocument({
    document,
    newValues,
  }: {
    document: GithubDocument;
    newValues: GithubDocumentValuesInput;
  }): Promise<GithubDocument> {
    const response = await UpdateGithubDocumentOperation.perform({
      input: {
        document: {
          id: document.id,
          new_values: newValues,
        },
      },
      origin: appConfig.eaveOrigin,
      teamId: this.team.id,
      ctx: this.ctx,
    });

    this.setGithubDocument({ document: response.document });
    return response.document;
  }

  setGithubDocument({ document }: { document: GithubDocument }) {
    if (document.file_path !== null) {
      // TODO: What to do if it's null?
      const key = githubDocumentKey({
        filePath: document.file_path,
        externalRepoId: this.eaveGithubRepo.external_repo_id,
      });
      this.eaveGithubDocuments[key] = document;
    }
  }

  getGithubDocument({
    filePath,
  }: {
    filePath: string;
  }): GithubDocument | undefined {
    const key = githubDocumentKey({
      filePath,
      externalRepoId: this.eaveGithubRepo.external_repo_id,
    });
    return this.eaveGithubDocuments[key];
  }
}

function githubDocumentKey({
  externalRepoId,
  filePath,
}: {
  externalRepoId: string;
  filePath: string;
}): string {
  return `${externalRepoId}/${filePath}`;
}
