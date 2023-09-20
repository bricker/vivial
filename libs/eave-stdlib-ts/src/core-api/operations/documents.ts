import { sharedConfig } from '../../config.js';
import { EaveApp } from '../../eave-origins.js';
import { CtxArg, RequestArgsOrigin, RequestArgsTeamId, makeRequest } from '../../requests.js';
import { DocumentInput, DocumentSearchResult } from '../models/documents.js';
import { DocumentReference, Subscription } from '../models/subscriptions.js';
import { Team } from '../models/team.js';
import { CoreApiEndpointConfiguration } from './shared.js';

export type UpsertDocumentRequestBody = {
  document: DocumentInput;
  subscriptions: Array<Subscription>;
}
export type UpsertDocumentResponseBody = {
  team: Team;
  subscriptions: Array<Subscription>;
  document_reference: DocumentReference;
}

export class UpsertDocumentOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/documents/upsert" })

  static async perform(args: RequestArgsTeamId & {input: UpsertDocumentRequestBody}): Promise<UpsertDocumentResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <UpsertDocumentResponseBody>(await resp.json());
    return responseData;
  }
}

export type SearchDocumentsRequestBody = {
  query: string;
}

export type SearchDocumentsResponseBody = {
  team: Team;
  documents: DocumentSearchResult[];
}

export class SearchDocumentsOperation {
  static config = new CoreApiEndpointConfiguration({ path: "/documents/search" })

  static async perform(args: RequestArgsTeamId & {input: SearchDocumentsRequestBody}): Promise<SearchDocumentsResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <SearchDocumentsResponseBody>(await resp.json());
    return responseData;
  }
}

