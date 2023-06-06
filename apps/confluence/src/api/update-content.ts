import { v4 as uuidv4 } from 'uuid';
import { RequestResponse } from 'request';
import { Request, Response } from 'express';
import { AddOn, HostClient } from 'atlassian-connect-express';
import { CreateContentRequestBody, CreateContentResponseBody, SearchContentRequestBody, SearchContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResult, ConfluenceSpace } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { getAuthedConnectClient } from './util.js';
import { createPage, getPageByTitle, getPageChildren, getSpaceByKey, getSpaceRootPages } from '../confluence-client.js';
import { DocumentInput } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/documents.js';


export default async function updateContent(req: Request, res: Response, addon: AddOn) {
}

// async def update_document(
//   self,
//   input: DocumentInput,
//   document_id: str,
// ) -> abstract.DocumentMetadata:
//   """
//   Update an existing Confluence document with the new body.
//   Notably, the title and parent are not changed.
//   """
//   existing_page = await self._get_confluence_page_by_id(document_id=document_id)
//   if existing_page is None:
//       # TODO: This page was probably deleted. Remove it from our database?
//       raise NotImplementedError()

//   # TODO: Use a different body format? Currently it will probably return the "storage" format,
//   # which is XML (HTML), and probably not great for an OpenAI prompt.
//   if existing_page.body is not None and existing_page.body.content is not None:
//       # TODO: Token counting
//       prompt = (
//           "Merge the following two documents."
//           "\n\n"
//           "First Document:\n"
//           "=========================\n"
//           f"{existing_page.body.content}\n"
//           "=========================\n\n"
//           "Second Document:\n"
//           "=========================\n"
//           f"{input.content}\n"
//           "=========================\n"
//       )
//       openai_params = eave.stdlib.openai_client.ChatCompletionParameters(
//           temperature=0.2,
//           messages=[prompt],
//       )
//       resolved_document_body = await eave.stdlib.openai_client.chat_completion(params=openai_params)

//       if resolved_document_body is None:
//           raise OpenAIDataError()

//   else:
//       resolved_document_body = input.content

//   content = clean_document(raw_doc=resolved_document_body)
//   response = self._confluence_client.update_page(
//       page_id=document_id,
//       title=existing_page.title,
//       body=content,
//   )

//   if response is None:
//       raise ConfluenceDataError("confluence update_page response")

//   json = cast(eave.stdlib.typing.JsonObject, response)
//   page = eave.stdlib.atlassian.ConfluencePage(json)
//   base_url = self.oauth_session.confluence_context.base_url
//   return abstract.DocumentMetadata(
//       id=page.id or "",
//       url=page.canonical_url(base_url),
//   )
