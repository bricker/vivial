import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { DeleteContentRequestBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import ConfluenceClient from '../confluence-client.js';

export default async function deleteContent(req: Request, res: Response, addon: AddOn) {
  const client = await ConfluenceClient.getAuthedConnectClient(req, addon);
  const { content } = <DeleteContentRequestBody>req.body;
  await client.archivePage({ contentId: content.content_id });
}
