import { RequestResponse } from 'request';
import { Request, Response } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { SearchContentRequestBody, SearchContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { ConfluenceSearchResult } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { getAuthedConnectClient } from './util.js';
import { search } from '../confluence-client.js';

export default async function searchContent(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const requestBody = <SearchContentRequestBody>req.body;

  const { space_key, text } = requestBody.search_params;
  const cqlConditions: string[] = [];
  let cqlcontext: string | undefined;

  if (space_key !== undefined) {
    cqlcontext = JSON.stringify({ spaceKey: space_key });
  }
  if (text.length > 0) {
    cqlConditions.push(`text ~ "${text}"`);
  }

  const cql = cqlConditions.join(' AND ');

  if (cql.length === 0) {
    eaveLogger.error({ message: 'Invalid CQL', cql, cqlcontext });
    res.status(500);
    return;
  }

  const results = await search({ client, cql, cqlcontext });
  // Remove pages with no body
  const filteredResults = results.filter((r) => r.content?.body?.content);
  const responseBody: SearchContentResponseBody = {
    results: filteredResults,
  };

  res.json(responseBody);
}
