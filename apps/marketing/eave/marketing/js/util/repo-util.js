export function mapReposByExternalId(repoList) {
  const repoMap = {};
  for (const repo of repoList) {
    const externalId = repo["external_repo_id"];
    repoMap[externalId] = repo;
  }
  return repoMap;
}
