import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { DocumentInput, DocumentSearchResult } from '../models/documents.js';
import { DocumentReference, Subscription } from '../models/subscriptions.js';
import { Team } from '../models/team.js';
import { CORE_API_BASE_URL } from './shared.js';

export type UpsertDocumentRequestBody = {
  document: DocumentInput;
  subscriptions: Array<Subscription>;
}
export type UpsertDocumentResponseBody = {
  team: Team;
  subscriptions: Array<Subscription>;
  document_reference: DocumentReference;
}

export async function upsertDocument(args: RequestArgsTeamId & {input: UpsertDocumentRequestBody}): Promise<UpsertDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${CORE_API_BASE_URL}/documents/upsert`,
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

export async function searchDocuments(args: RequestArgsTeamId & {input: SearchDocumentsRequestBody}): Promise<SearchDocumentsResponseBody> {
  const resp = await makeRequest({
    url: `${CORE_API_BASE_URL}/documents/search`,
    ...args,
  });
  const responseData = <SearchDocumentsResponseBody>(await resp.json());
  return responseData;
}
