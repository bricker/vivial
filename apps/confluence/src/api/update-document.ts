import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import { WebTriggerRequestPayload, WebTriggerResponsePayload } from '../types';
import { makeResponse } from '../response';

export default async function updateDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  eaveLogger.info('updateDocument', request);
  return makeResponse();
}
