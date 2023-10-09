import { UUID } from "../../types.js";

export enum Feature {
  API_DOCUMENTATION = "api_documentation",
  INLINE_CODE_DOCUMENTATION = "inline_code_documentation",
  ARCHITECTURE_DOCUMENTATION = "architecture_documentation",
}

export enum State {
  DISABLED = "disabled",
  ENABLED = "enabled",
  PAUSED = "paused",
}

export type GithubRepo = {
  team_id: UUID;
  id: UUID;
  external_repo_id: string;
  display_name: string | null;
  api_documentation_state: State;
  inline_code_documentation_state: State;
  architecture_documentation_state: State;
};

export type GithubRepoCreateInput = {
  external_repo_id: string;
  display_name: string;
  api_documentation_state: State;
  inline_code_documentation_state: State;
  architecture_documentation_state: State;
};

export type GithubRepoRefInput = {
  id: UUID;
};

export type GithubRepoListInput = {
  external_repo_id: string;
};

export type GithubRepoUpdateValues = {
  api_documentation_state?: State;
  inline_code_documentation_state?: State;
  architecture_documentation_state?: State;
};

export type GithubRepoUpdateInput = {
  id: UUID;
  new_values: GithubRepoUpdateValues;
};

export type GithubReposDeleteInput = {
  id: UUID;
};

export type GithubReposFeatureStateInput = {
  feature: Feature;
  state: State;
};
