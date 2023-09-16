// Source response object defined in Github API
// https://docs.github.com/en/rest/repos/repos?apiVersion=2022-11-28#get-a-repository
export type GithubRepository = {
  node_id: string;
  full_name: string;
}

export type GithubRepoInput = {
  external_repo_id: string;
}
