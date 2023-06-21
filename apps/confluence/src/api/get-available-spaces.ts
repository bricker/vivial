import { GetAvailableSpacesResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import { ExpressHandlerArgs } from '@eave-fyi/eave-stdlib-ts/src/requests.js';
import { ConfluenceClientArg } from './util.js';

export default async function getAvailableSpaces({ res, confluenceClient }: ExpressHandlerArgs & ConfluenceClientArg) {
  const spaces = await confluenceClient.getSpaces();

  const responseBody: GetAvailableSpacesResponseBody = {
    confluence_spaces: spaces,
  };

  res.json(responseBody);
}
