import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { makeRequest, RequestArgsAuthedRequest } from '../../requests.js';
import {
  GithubDocument,
  GithubDocumentCreateInput,
  GithubDocumentsDeleteByIdsInput,
  GithubDocumentsDeleteByTypeInput,
  GithubDocumentsQueryInput,
  GithubDocumentUpdateInput,
} from '../models/github-documents.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type GetGithubDocumentsRequestBody = {
  query_params: GithubDocumentsQueryInput;
}

export type GetGithubDocumentsResponseBody = {
  documents: Array<GithubDocument>;
}

export async function getGithubDocuments(
  args: RequestArgsAuthedRequest & { input: GetGithubDocumentsRequestBody },
): Promise<GetGithubDocumentsResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-documents/query`,
    ...args,
  });
  const responseData = <GetGithubDocumentsResponseBody>(await resp.json());
  return responseData;
}

export type CreateGithubDocumentRequestBody = {
  document: GithubDocumentCreateInput;
}

export type CreateGithubDocumentResponseBody = {
  document: GithubDocument;
}

export async function createGithubDocument(
  args: RequestArgsAuthedRequest & { input: CreateGithubDocumentRequestBody },
): Promise<CreateGithubDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-documents/create`,
    ...args,
  });
  const responseData = <CreateGithubDocumentResponseBody>(await resp.json());
  return responseData;
}

export type UpdateGithubDocumentRequestBody = {
  document: GithubDocumentUpdateInput;
}

export type UpdateGithubDocumentResponseBody = {
  document: GithubDocument;
}

export async function updateGithubDocument(
  args: RequestArgsAuthedRequest & { input: UpdateGithubDocumentRequestBody },
): Promise<UpdateGithubDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/github-documents/update`,
    ...args,
  });
  const responseData = <UpdateGithubDocumentResponseBody>(await resp.json());
  return responseData;
}

export type DeleteGithubDocumentsByIdsRequestBody = {
  documents: Array<GithubDocumentsDeleteByIdsInput>;
}

export async function deleteGithubDocumentsByIds(
  args: RequestArgsAuthedRequest & { input: DeleteGithubDocumentsByIdsRequestBody },
): Promise<void> {
  await makeRequest({
    url: `${baseUrl}/github-documents/delete/id`,
    ...args,
  });
}

export type DeleteGithubDocumentsByTypeRequestBody = {
  documents: Array<GithubDocumentsDeleteByTypeInput>;
}

export async function deleteGithubDocumentsByType(
  args: RequestArgsAuthedRequest & { input: DeleteGithubDocumentsByTypeRequestBody },
): Promise<void> {
  await makeRequest({
    url: `${baseUrl}/github-documents/delete/type`,
    ...args,
  });
}
