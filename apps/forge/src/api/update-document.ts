import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { WebTriggerRequestPayload, WebTriggerResponsePayload } from '../types.js';
import { makeResponse } from '../response.js';

export default async function updateDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  eaveLogger.info('updateDocument', request);
  return makeResponse();
}
