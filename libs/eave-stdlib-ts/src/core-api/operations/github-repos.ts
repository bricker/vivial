import { sharedConfig } from '../../config.js';
import { EaveService } from '../../eave-origins.js';
import { makeRequest, RequestArgsAuthedRequest } from '../../requests.js';
import {
  GithubRepo,
  GithubRepoCreateInput,
  GithubRepoListInput,
  GithubReposDeleteInput,
  GithubReposFeatureStateInput,
  GithubRepoUpdateInput,
} from '../models/github-repos.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveService.api);

export type GetGithubReposRequestBody = {
  repos: GithubRepoListInput;
}

export type GetGithubReposResponseBody = {
  repos: Array<GithubRepo>;
}

export async function getGithubRepos(
  args: RequestArgsAuthedRequest & { input: GetGithubReposRequestBody },
): Promise<GetGithubReposResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-repos/query`,
    ...args,
  });
  const responseData = <GetGithubReposResponseBody>(await resp.json());
  return responseData;
}

export type FeatureStateGithubReposRequestBody = {
  query_params: GithubReposFeatureStateInput;
}

export type FeatureStateGithubReposResponseBody = {
  states_match: boolean;
}

export async function queryGithubReposFeatureState(
  args: RequestArgsAuthedRequest & { input: FeatureStateGithubReposRequestBody },
): Promise<FeatureStateGithubReposResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-repos/query/enabled`,
    ...args,
  });
  const responseData = <FeatureStateGithubReposResponseBody>(await resp.json());
  return responseData;
}

export type CreateGithubRepoRequestBody = {
  repo: GithubRepoCreateInput;
}

export type CreateGithubRepoResponseBody = {
  repo: GithubRepo;
}

export async function createGithubRepo(
  args: RequestArgsAuthedRequest & { input: CreateGithubRepoRequestBody },
): Promise<CreateGithubRepoResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-repos/create`,
    ...args,
  });
  const responseData = <CreateGithubRepoResponseBody>(await resp.json());
  return responseData;
}

export type DeleteGithubReposRequestBody = {
  repos: GithubReposDeleteInput;
}

export async function deleteGithubRepos(
  args: RequestArgsAuthedRequest & { input: DeleteGithubReposRequestBody },
): Promise<void> {
  await makeRequest({
    url: `${baseUrl}/github-repos/delete`,
    ...args,
  });
}

export type UpdateGithubReposRequestBody = {
  repos: Array<GithubRepoUpdateInput>;
}

export type UpdateGithubReposResponseBody = {
  repos: Array<GithubRepo>;
}

export async function updateGithubRepos(
  args: RequestArgsAuthedRequest & { input: UpdateGithubReposRequestBody },
): Promise<UpdateGithubReposResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-repos/update`,
    ...args,
  });
  const responseData = <UpdateGithubReposResponseBody>(await resp.json());
  return responseData;
}
