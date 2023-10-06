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
  team_id: string;
  external_repo_id: string;
  github_installation_id: string;
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

export type GithubRepoListInput = {
  external_repo_id: string;
};

export type GithubRepoUpdateValues = {
  api_documentation_state?: State;
  inline_code_documentation_state?: State;
  architecture_documentation_state?: State;
};

export type GithubRepoUpdateInput = {
  external_repo_id: string;
  new_values: GithubRepoUpdateValues;
};

export type GithubReposDeleteInput = {
  external_repo_id: string;
};

export type GithubReposFeatureStateInput = {
  feature: Feature;
  state: State;
};
