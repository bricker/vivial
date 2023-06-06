import { ConfluenceBodyCreateStorage, ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluenceContentType, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResult, ConfluenceSpace, ConfluenceSpaceContentDepth, ConfluenceSpaceStatus, ConfluenceSpaceType, SystemInfoEntity } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { DocumentReferenceInput } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/subscriptions.js';
import { HostClient } from 'atlassian-connect-express';
import { RequestResponse } from 'request';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { cleanDocument } from './api/util.js';

/*
https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
*/
export async function getSpaceByKey({ client, spaceKey }: { client: HostClient, spaceKey: string }): Promise<ConfluenceSpace | null> {
  const request = {
    url: '/api/v2/spaces',
    qs: {
      keys: [spaceKey],
      type: ConfluenceSpaceType.global,
      status: ConfluenceSpaceStatus.current,
    },
  };
  eaveLogger.debug({ message: 'getSpaceByKey request', request });

  const response: RequestResponse = await client.get(request);
  eaveLogger.debug({ message: 'getSpaceByKey response', response });
  const body = JSON.parse(response.body);

  const results = <ConfluenceSpace[]>body.results;
  return results[0] || null;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-get
*/
export async function getPageByTitle({ client, space, title }: { client: HostClient, space: ConfluenceSpace, title: string }): Promise<ConfluencePage | null> {
  const request = {
    url: '/rest/api/content',
    qs: {
      type: 'page',
      space: space.key,
      title,
    },
  };
  eaveLogger.debug({ message: 'getPageByTitle request', request });

  const response: RequestResponse = await client.get(request);
  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'getPageByTitle response', body });

  const results = <ConfluencePage[]>body.results;
  return results[0] || null;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-get
*/
export async function getPageById({ client, pageId }: { client: HostClient, pageId: string }): Promise<ConfluencePage> {
  const request = {
    url: `/wiki/rest/api/content/${pageId}`,
  };
  eaveLogger.debug({ message: 'getPageById request', request });

  const response: RequestResponse = await client.get(request);
  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'getPageById response', body });

  const page = <ConfluencePage>body;
  return page;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content---children-and-descendants/#api-wiki-rest-api-content-id-child-type-get
*/
export async function getPageChildren({ client, pageId }: { client: HostClient, pageId: string }): Promise<ConfluencePage[]> {
  const request = {
    url: `/wiki/rest/api/content/${pageId}/child/${ConfluenceContentType.page}`,
    qs: {
      limit: 100, // TODO: Pagination
    },
  };
  eaveLogger.debug({ message: 'getPageChildren request', request });

  const response: RequestResponse = await client.get(request);
  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'getPageChildren response', body });

  const results = <ConfluencePage[]>body.results;
  return results;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-spacekey-content-type-get
*/
export async function getSpaceRootPages({ client, space }: { client: HostClient, space: ConfluenceSpace }): Promise<ConfluencePage[]> {
  const request = {
    url: `/wiki/rest/api/space/${space.key}/content/${ConfluenceContentType.page}`,
    qs: {
      depth: ConfluenceSpaceContentDepth.root,
      limit: 100, // TODO: Pagination
    },
  };
  eaveLogger.debug({ message: 'getSpaceRootPages request', request });

  const response: RequestResponse = await client.get(request);
  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'getSpaceRootPages response', body });

  const results = <ConfluencePage[]>body.results;
  return results;
}

/* https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post */
export async function createPage({ client, space, body, title, parentId }: { client: HostClient, space: ConfluenceSpace, title: string, body: string, parentId?: string }): Promise<ConfluencePage> {
  const pageBody: ConfluencePageBodyWrite = {
    representation: ConfluenceContentBodyRepresentation.storage,
    value: cleanDocument(body),
  };

  const request = {
    url: '/api/v2/pages',
    json: true,
    body: {
      spaceId: space.id,
      status: ConfluenceContentStatus.current,
      title,
      body: pageBody,
      parentId,
    },
  };
  eaveLogger.debug({ message: 'createPage request', request });

  const response: RequestResponse = await client.post(request);
  const responseBody = JSON.parse(response.body);
  eaveLogger.debug({ message: 'createPage response', body: responseBody });

  const page = <ConfluencePage>responseBody;
  return page;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-archive-post
*/
export async function archivePage({ client, contentId }: { client: HostClient, contentId: string }) {
  const request = {
    url: '/rest/api/content/archive',
    json: true,
    body: {
      pages: [
        { id: contentId },
      ],
    },
  };
  eaveLogger.debug({ message: 'archivePage request', request });
  await client.post(request);
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
*/
export async function getSpaces({ client }: { client: HostClient }): Promise<ConfluenceSpace[]> {
  const request = {
    url: '/rest/api/space',
    qs: {
      status: ConfluenceSpaceStatus.current,
      type: ConfluenceSpaceType.global,
    },
  };
  eaveLogger.debug({ message: 'getSpaces request', request });

  const response: RequestResponse = await client.get(request);
  eaveLogger.debug({ message: 'getSpaces response', body: response.body });
  const body = JSON.parse(response.body);

  const spaces = <ConfluenceSpace[]>body.results;
  return spaces;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-search/#api-wiki-rest-api-search-get
*/
export async function search({ client, cql, cqlcontext }: { client: HostClient, cql: string, cqlcontext?: string }): Promise<ConfluenceSearchResult[]> {
  const request = {
    url: '/rest/api/content/search',
    qs: { cql, cqlcontext },
  };
  eaveLogger.debug({ message: 'search request', request });

  const response: RequestResponse = await client.get(request);
  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'search response', body });

  const results = <ConfluenceSearchResult[]>body.results;
  return results;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-id-put
*/
export async function updatePage({ client, page, body }: { client: HostClient, page: ConfluencePage, body: string }): Promise<ConfluencePage> {
  let currentVersion = page.version?.number;
  if (currentVersion === undefined) {
    currentVersion = 0;
  }

  const newBody: ConfluenceBodyCreateStorage = {
    value: body,
    represenation: ConfluenceContentBodyRepresentation.storage,
  };

  const request = {
    url: `/wiki/rest/api/content/${page.id}`,
    json: true,
    body: {
      version: currentVersion + 1,
      title: page.title,
      type: page.type,
      body: newBody,
    },
  };
  eaveLogger.debug({ message: 'updatePage request', request });

  const response: RequestResponse = await client.put(request);

  const responseBody = JSON.parse(response.body);
  eaveLogger.debug({ message: 'updatePage response', body: responseBody });

  return <ConfluencePage>responseBody;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-settings/#api-wiki-rest-api-settings-systeminfo-get
*/
export async function getSystemInfo({ client }: {client: HostClient}): Promise<SystemInfoEntity> {
  const request = {
    url: '/rest/api/settings/systemInfo',
  };
  eaveLogger.debug({ message: 'getSystemInfo request', request });

  const response: RequestResponse = await client.put(request);

  const body = JSON.parse(response.body);
  eaveLogger.debug({ message: 'getSystemInfo response ', body });

  return <SystemInfoEntity>body;
}
