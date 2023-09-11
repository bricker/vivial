export enum Status {
  PROCESSING = 'processing',
  PR_OPENED = 'pr_opened',
  PR_MERGED = 'pr_merged',
}

export enum DocumentType {
  API_DOCUMENT = 'api_document',
  ARCHITECTURE_DOCUMENT = 'architecture_document',
}

export type GithubDocument = {
  id: string;
  team_id: string;
  external_repo_id: string;
  pull_request_number?: number;
  status: Status;
  status_updated: Date;
  file_path?: string;
  api_name?: string;
  type: DocumentType;
}

export type GithubDocumentsQueryInput = {
  id?: string;
  external_repo_id?: string;
  type?: DocumentType;
}

export type GithubDocumentCreateInput = {
  external_repo_id: string;
  file_path?: string;
  api_name?: string;
  type: DocumentType;
  pull_request_number?: number;
}

export type GithubDocumentValuesInput = {
  pull_request_number?: number;
  status?: Status;
  file_path?: string;
  api_name?: string;
}

export type GithubDocumentUpdateInput = {
  id: string;
  new_values: GithubDocumentValuesInput;
}

export type GithubDocumentDeleteInput = {
  id: string;
}
