import { SearchContentRequestBody, SearchContentResponseBody } from "@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js";
import eaveLogger, { LogContext } from "@eave-fyi/eave-stdlib-ts/src/logging.js";
import { ExpressHandlerArgs } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { ConfluenceClientArg } from "./util.js";

export default async function searchContent({ req, res, confluenceClient }: ExpressHandlerArgs & ConfluenceClientArg) {
  const ctx = LogContext.load(res);
  const requestBody = <SearchContentRequestBody>req.body;

  const { space_key, text } = requestBody.search_params;
  const cqlConditions: string[] = [];
  let cqlcontext: { [key: string]: any } = {};

  if (space_key !== undefined) {
    cqlcontext = {
      spaceKey: space_key,
    };
  }
  if (text.length > 0) {
    cqlConditions.push(`text ~ "${text}"`);
  }

  const cql = cqlConditions.join(" AND ");

  if (cql.length === 0) {
    eaveLogger.error("Invalid CQL", { cql, cqlcontext }, ctx);
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
