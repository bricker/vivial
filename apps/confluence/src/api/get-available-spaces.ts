import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { GetAvailableSpacesResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import { ConfluenceSpace } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { getAuthedConnectClient } from './util.js';
import { RequestResponse } from 'request';
import { getSpaces } from '../confluence-client.js';

export default async function getAvailableSpaces(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const spaces = await getSpaces({client});

  const responseBody: GetAvailableSpacesResponseBody = {
    confluence_spaces: spaces,
  };

  res.json(responseBody);
}
