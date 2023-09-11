export enum Feature {
  API_DOCUMENTATION = 'api_documentation',
  INLINE_CODE_DOCUMENTATION = 'inline_code_documentation',
  ARCHITECTURE_DOCUMENTATION = 'architecture_documentation',
}

export enum State {
  DISABLED = 'disabled',
  ENABLED = 'enabled',
  PAUSED = 'paused',
}

export type GithubRepo = {
  team_id: string;
  external_repo_id: string;
  api_documentation_state: State;
  inline_code_documentation_state: State;
  architecture_documentation_state: State;
}

export type GithubRepoCreateInput = {
  external_repo_id: string;
  api_documentation_state: State;
  inline_code_documentation_state: State;
  architecture_documentation_state: State;
}

export type GithubRepoListInput = {
  /** List of ids to filter by. Provide empty list to fetch all repos. */
  external_repo_ids: Array<string>;
}

export type GithubRepoUpdateValues = {
  api_documentation_state?: State;
  inline_code_documentation_state?: State;
  architecture_documentation_state?: State;
}

export type GithubRepoUpdateInput = {
  external_repo_id: string;
  new_values: GithubRepoUpdateValues;
}

export type GithubReposDeleteInput = {
  external_repo_ids: Array<string>;
}

export type GithubReposFeatureStateInput = {
  feature: Feature;
  state: State;
}
