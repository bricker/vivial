import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../../requests.js';
import { DocumentInput, DocumentSearchResult } from '../models/documents.js';
import { DocumentReference, Subscription } from '../models/subscriptions.js';
import { Team } from '../models/team.js';

const baseUrl = sharedConfig.eaveInternalServiceBase(EaveApp.eave_api);

export type UpsertDocumentRequestBody = {
  document: DocumentInput;
  subscriptions: Array<Subscription>;
}
export type UpsertDocumentResponseBody = {
  team: Team;
  subscriptions: Array<Subscription>;
  document_reference: DocumentReference;
}

export async function upsertDocument(args: RequestArgsOriginAndTeamId & {input: UpsertDocumentRequestBody}): Promise<UpsertDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/documents/upsert`,
    ...args,
  });
  const responseData = <UpsertDocumentResponseBody>(await resp.json());
  return responseData;
}

export type SearchDocumentsRequestBody = {
  query: string;
}

export type SearchDocumentsResponseBody = {
  team: Team;
  documents: DocumentSearchResult[];
}

export async function searchDocuments(args: RequestArgsOriginAndTeamId & {input: SearchDocumentsRequestBody}): Promise<SearchDocumentsResponseBody> {
  const resp = await makeRequest({
    url: `${baseUrl}/documents/search`,
    ...args,
  });
  const responseData = <SearchDocumentsResponseBody>(await resp.json());
  return responseData;
}
