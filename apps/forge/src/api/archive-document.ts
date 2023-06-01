import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { WebTriggerRequestPayload, WebTriggerResponsePayload } from '../types.js';
import { makeResponse } from '../response.js';

export default async function archiveDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  eaveLogger.info('archiveDocument', request);
  return makeResponse();
}
