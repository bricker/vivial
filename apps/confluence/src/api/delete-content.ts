// self._confluence_client.post("rest/api/content/archive", data={"pages": [{"id": int(document_id)}]})
import { v4 as uuidv4 } from 'uuid';
import { RequestResponse } from 'request';
import { Request, Response } from 'express';
import { AddOn, HostClient } from 'atlassian-connect-express';
import { CreateContentRequestBody, DeleteContentRequestBody, SearchContentRequestBody, SearchContentResponseBody } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/operations.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResult, ConfluenceSpace } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { getAuthedConnectClient } from './util.js';
import { archivePage, createPage, getPageByTitle, getPageChildren, getSpaceByKey, getSpaceRootPages } from '../confluence-client.js';
import { DocumentInput } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/documents.js';

export default async function deleteContent(req: Request, res: Response, addon: AddOn) {
  const client = await getAuthedConnectClient(req, addon);
  const { content } = <DeleteContentRequestBody>req.body;
  await archivePage({client, contentId: content.content_id});
}
