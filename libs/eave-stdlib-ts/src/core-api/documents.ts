import { sharedConfig } from '../config.js';
import { RequestArgsOriginAndTeamId, makeRequest } from '../lib/requests.js';
import { DocumentReference, Subscription } from './subscriptions.js';
import { Team } from './team.js';

export type DocumentInput = {
  title: string;
  content: string;
  parent?: DocumentInput;
}

export type EaveDocument = {
  title: string;
  content: string;
  parent?: EaveDocument;
}

export type UpsertDocumentRequestBody = {
  document: DocumentInput;
  subscriptions: Array<Subscription>;
}
export type UpsertDocumentResponseBody = {
  team: Team;
  subscriptions: Array<Subscription>;
  document_reference: DocumentReference;
}

export async function upsertDocument({ origin, teamId, input }: RequestArgsOriginAndTeamId & {input: UpsertDocumentRequestBody}): Promise<UpsertDocumentResponseBody> {
  const resp = await makeRequest({
    url: `${sharedConfig.eaveApiBase}/documents/upsert`,
    origin,
    input,
    teamId,
  });
  const responseData = <UpsertDocumentResponseBody>(await resp.json());
  return responseData;
}
