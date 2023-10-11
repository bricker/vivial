// @ts-check
import * as Types from "../types"; /**
 * Maps an array of Github repositories to an object with repository IDs as keys.
 *
 * @param {Types.GithubRepo[]} repoList - The list of Github repositories.
 * @returns {{[key: string] : Types.GithubRepo}} An object mapping repository IDs to their corresponding repository.
 */
// eslint-disable-line no-unused-vars

export function mapReposById(/** @type {Types.GithubRepo[]} */ repoList) {
  /** @type {{[key: string] : Types.GithubRepo}} */
  const repoMap = {};
  for (const repo of repoList) {
    const externalId = repo.id;
    repoMap[externalId] = repo;
  }
  return repoMap;
}
