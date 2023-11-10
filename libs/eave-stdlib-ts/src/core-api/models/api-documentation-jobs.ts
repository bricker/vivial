export type ApiDocumentationJob = {
  id: string;
  team_id: string;
  /** foreign key to github_repos.id */
  github_repo_id: string;
  state: string;
  last_result: string;
};

export enum LastJobResult {
  none = "none",
  doc_created = "doc_created",
  no_api_found = "no_api_found",
  error = "error",
}

export enum ApiDocumentationJobState {
  running = "running",
  idle = "idle",
}

export type ApiDocumentationJobListInput = {
  id: string;
};

export type ApiDocumentationJobUpsertInput = {
  github_repo_id: string;
  state: ApiDocumentationJobState;
  last_result?: LastJobResult; // TODO: does this need to be option?
};
