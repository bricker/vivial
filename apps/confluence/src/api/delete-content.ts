import { DeleteContentRequestBody } from "@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js";
import { ExpressHandlerArgs } from "@eave-fyi/eave-stdlib-ts/src/requests.js";
import { ConfluenceClientArg } from "./util.js";

export default async function deleteContent({
  req,
  confluenceClient,
}: ExpressHandlerArgs & ConfluenceClientArg) {
  const { content } = <DeleteContentRequestBody>req.body;
  await confluenceClient.archivePage({ contentId: content.content_id });
}
