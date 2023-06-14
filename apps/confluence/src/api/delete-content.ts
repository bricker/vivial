import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { DeleteContentRequestBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import ConfluenceClient from '../confluence-client.js';

export default async function deleteContent({ req, res, confluenceClient }: { req: Request, res: Response, confluenceClient: ConfluenceClient }) {
  const { content } = <DeleteContentRequestBody>req.body;
  await confluenceClient.archivePage({ contentId: content.content_id });
}
