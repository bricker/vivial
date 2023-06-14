import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { GetAvailableSpacesResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import ConfluenceClient from '../confluence-client.js';

export default async function getAvailableSpaces({ req, res, confluenceClient }: { req: Request, res: Response, confluenceClient: ConfluenceClient }) {
  const spaces = await confluenceClient.getSpaces();

  const responseBody: GetAvailableSpacesResponseBody = {
    confluence_spaces: spaces,
  };

  res.json(responseBody);
}
