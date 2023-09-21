// Source response object defined in Github API
// https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
export type GithubRepository = {
  node_id: string;
  full_name: string;
}

export type FileChange = {
  /**
   * path from github repo root to file to change
   */
  path: string,
  /**
   * base64 encoded string to replace the content of the file at `path`
   */
  contents: string,
};

export type GithubRepoInput = {
  external_repo_id: string;
}

export type ExternalGithubRepo = {
  id?: string;
  name?: string;
  url?: string;
  description?: string | null;
  createdAt?: string;
  updatedAt?: string;
  pushedAt?: string;
}