import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import { WebTriggerRequestPayload, WebTriggerResponsePayload } from '../types';
import { makeResponse } from '../response';

export default async function archiveDocument(request: WebTriggerRequestPayload): Promise<WebTriggerResponsePayload> {
  eaveLogger.info('archiveDocument', request);
  return makeResponse();
}
