import { Request, Response } from 'express';
import { SearchContentRequestBody, SearchContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { getEaveState } from '@eave-fyi/eave-stdlib-ts/src/lib/request-state.js';
import ConfluenceClient from '../confluence-client.js';

export default async function searchContent({ req, res, confluenceClient }: { req: Request, res: Response, confluenceClient: ConfluenceClient }) {
  const eaveState = getEaveState(res);
  const requestBody = <SearchContentRequestBody>req.body;

  const { space_key, text } = requestBody.search_params;
  const cqlConditions: string[] = [];
  let cqlcontext: {[key:string]: any} = {};

  if (space_key !== undefined) {
    cqlcontext = {
      spaceKey: space_key,
    };
  }
  if (text.length > 0) {
    cqlConditions.push(`text ~ "${text}"`);
  }

  const cql = cqlConditions.join(' AND ');

  if (cql.length === 0) {
    eaveLogger.error({ message: 'Invalid CQL', cql, cqlcontext, eaveState });
    res.sendStatus(500);
    return;
  }

  const results = await confluenceClient.search({ cql, cqlcontext });
  // Remove pages with no body
  const filteredResults = results.filter((r) => r.body?.storage?.value);

  const responseBody: SearchContentResponseBody = {
    results: filteredResults,
  };

  res.json(responseBody);
}
