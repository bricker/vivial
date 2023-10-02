import { Team } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/team.js";
import { GetTeamOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/team.js";
import { CtxArg } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { appConfig } from "../../config.js";
import { RunApiDocumentationTaskRequestBody } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js";
import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { GetGithubReposOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-repos.js";
import { eaveLogger } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import assert from "assert";
import { DocumentType, GithubDocument, GithubDocumentValuesInput, Status } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-documents.js";
import { CreateGithubDocumentOperation, GetGithubDocumentsOperation, UpdateGithubDocumentOperation } from "@eave-fyi/eave-stdlib-ts/src/core-api/operations/github-documents.js";
import { ExpressAPI } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { GConstructor } from "@eave-fyi/eave-stdlib-ts/src/types.js";
import { ExpressAPIDocumentorBase, ExpressAPIDocumentorBaseMixin } from "./base.js";
import { GithubAPIHelperMixin } from "./github-api.js";

function CoreAPIHelperClassFactory<TBase extends ExpressAPIDocumentorBaseMixin>(Base: TBase) {
  return class extends Base {
    async getTeam({
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

    async getRepo({
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

    async getExistingGithubDocuments({
      team,
      repo,
      ctx,
    }: CtxArg & { team: Team; repo: GithubRepo }): Promise<GithubDocument[]> {
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

      return getDocResponse.documents;
    }

    async createPlaceholderGithubDocument({
      apiInfo,
      team,
      repo,
      ctx,
    }: CtxArg & { apiInfo: ExpressAPI, team: Team; repo: GithubRepo }): Promise<GithubDocument> {
      const createDocResponse = await CreateGithubDocumentOperation.perform({
        origin: appConfig.eaveOrigin,
        ctx,
        teamId: team.id,
        input: {
          document: {
            external_repo_id: repo.external_repo_id,
            type: DocumentType.API_DOCUMENT,
            status: Status.PROCESSING,
            api_name: apiInfo.name || null,
            file_path: apiInfo.documentationFilePath || null,
            pull_request_number: null,
          },
        },
      });

      return createDocResponse.document;
    }

    async updateGithubDocument({
      team,
      document,
      newValues,
      ctx,
    }: CtxArg & {
      team: Team;
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
        teamId: team.id,
        ctx,
      });

      return response.document
    }
  }
}

export const CoreAPIHelperMixin = CoreAPIHelperClassFactory(ExpressAPIDocumentorBase);
