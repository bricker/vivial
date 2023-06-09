import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { DeleteContentRequestBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getAuthedConnectClient } from './util.js';
import { archivePage } from '../confluence-client.js';

export default async function deleteContent(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const { content } = <DeleteContentRequestBody>req.body;
  await archivePage({ client, contentId: content.content_id });
}
