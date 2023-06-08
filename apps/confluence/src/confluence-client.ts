import { ConfluenceContentBody, ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluenceContentType, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResultWithBody, ConfluenceSpace, ConfluenceSpaceContentDepth, ConfluenceSpaceStatus, ConfluenceSpaceType, SystemInfoEntity } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { HostClient } from 'atlassian-connect-express';
import { RequestResponse } from 'request';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { cleanDocument } from './api/util.js';

/*
https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
*/
export async function getSpaceByKey({ client, spaceKey }: { client: HostClient, spaceKey: string }): Promise<ConfluenceSpace | null> {
  const request = {
    url: `/rest/api/space/${spaceKey}`,
  };
  logRequest('getSpaceByKey', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getSpaceByKey', response);
  if (response.statusCode >= 400) {
    return null;
  }

  const body = JSON.parse(response.body);
  const space = <ConfluenceSpace>body;
  return space;
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
  logRequest('getPageByTitle', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getPageByTitle', response);
  if (response.statusCode >= 400) {
    return null;
  }

  const body = JSON.parse(response.body);
  const results = <ConfluencePage[]>body.results;
  return results[0] || null;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-get
*/
export async function getPageById({ client, pageId }: { client: HostClient, pageId: string }): Promise<ConfluencePage | null> {
  const request = {
    url: `/rest/api/content/${pageId}`,
  };
  logRequest('getPageById', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getPageById', response);
  if (response.statusCode >= 400) {
    return null;
  }

  const body = JSON.parse(response.body);
  const page = <ConfluencePage>body;
  return page;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content---children-and-descendants/#api-wiki-rest-api-content-id-child-type-get
*/
export async function getPageChildren({ client, pageId }: { client: HostClient, pageId: string }): Promise<ConfluencePage[]> {
  const request = {
    url: `/rest/api/content/${pageId}/child/${ConfluenceContentType.page}`,
    qs: {
      limit: 100, // TODO: Pagination
    },
  };
  logRequest('getPageChildren', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getPageChildren', response);
  if (response.statusCode >= 400) {
    return [];
  }

  const body = JSON.parse(response.body);
  const results = <ConfluencePage[]>body.results;
  return results;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-spacekey-content-type-get
*/
export async function getSpaceRootPages({ client, space }: { client: HostClient, space: ConfluenceSpace }): Promise<ConfluencePage[]> {
  const request = {
    url: `/rest/api/space/${space.key}/content/${ConfluenceContentType.page}`,
    qs: {
      depth: ConfluenceSpaceContentDepth.root,
      limit: 100, // TODO: Pagination
    },
  };
  logRequest('getSpaceRootPages', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getSpaceRootPages', response);
  if (response.statusCode >= 400) {
    return [];
  }

  const body = JSON.parse(response.body);
  const results = <ConfluencePage[]>body.results;
  return results;
}

/* https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post */
export async function createPage({ client, space, body, title, parentId }: { client: HostClient, space: ConfluenceSpace, title: string, body: string, parentId?: string }): Promise<ConfluencePage | null> {
  const pageBody: ConfluencePageBodyWrite = {
    representation: ConfluenceContentBodyRepresentation.storage,
    value: cleanDocument(body),
  };

  let ancestors: {id: string}[] | undefined;
  if (parentId !== undefined) {
    ancestors = [{ id: parentId }];
  }

  const request = {
    url: '/rest/api/content',
    json: true,
    body: {
      title,
      type: ConfluenceContentType.page,
      space: {
        id: space.id,
      },
      status: ConfluenceContentStatus.current,
      body: {
        storage: pageBody,
      },
      ancestors,
    },
  };

  logRequest('createPage', request);

  const response: RequestResponse = await client.post(request);
  logResponse('createPage', response);
  if (response.statusCode >= 400) {
    return null;
  }

  const page = <ConfluencePage>response.body;
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
  logRequest('archivePage', request);
  const response: RequestResponse = await client.post(request);
  logResponse('archivePage', response);
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
  logRequest('getSpaces', request);

  const response: RequestResponse = await client.get(request);
  logResponse('getSpaces', response);
  if (response.statusCode >= 400) {
    return [];
  }

  const body = JSON.parse(response.body);
  const spaces = <ConfluenceSpace[]>body.results;
  return spaces;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-search/#api-wiki-rest-api-search-get
*/
export async function search({ client, cql, cqlcontext }: { client: HostClient, cql: string, cqlcontext?: {[key: string]: any} }): Promise<ConfluenceSearchResultWithBody[]> {
  const request = {
    url: '/rest/api/content/search',
    qs: {
      cql,
      cqlcontext: cqlcontext ? JSON.stringify(cqlcontext) : undefined,
      expand: ['body.storage'],
    },
  };
  logRequest('search', request);

  const response: RequestResponse = await client.get(request);
  logResponse('search', response);
  if (response.statusCode >= 400) {
    return [];
  }

  const body = JSON.parse(response.body);
  const results = <ConfluenceSearchResultWithBody[]>body.results;
  return results;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-id-put
*/
export async function updatePage({ client, page, body }: { client: HostClient, page: ConfluencePage, body: string }): Promise<ConfluencePage | null> {
  let currentVersion = page.version?.number;
  if (currentVersion === undefined) {
    currentVersion = 0;
  }

  const newBody: ConfluenceContentBody = {
    value: cleanDocument(body),
    representation: ConfluenceContentBodyRepresentation.storage,
  };

  const request = {
    url: `/rest/api/content/${page.id}`,
    json: true,
    body: {
      version: {
        number: currentVersion + 1,
        message: 'Update from Eave',
      },
      title: page.title,
      type: page.type,
      status: ConfluenceContentStatus.current,
      body: {
        storage: newBody,
      },
    },
  };
  logRequest('updatePage', request);

  const response: RequestResponse = await client.put(request);
  logResponse('updatePage', response);
  if (response.statusCode >= 400) {
    return null;
  }

  return <ConfluencePage>response.body;
}

/*
https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-settings/#api-wiki-rest-api-settings-systeminfo-get
*/
export async function getSystemInfo({ client }: {client: HostClient}): Promise<SystemInfoEntity | null> {
  const request = {
    url: '/rest/api/settings/systemInfo',
  };
  logRequest('getSystemInfo', request);

  const response: RequestResponse = await client.put(request);
  logResponse('getSystemInfo', response);
  if (response.statusCode >= 400) {
    return null;
  }

  const body = JSON.parse(response.body);
  return <SystemInfoEntity>body;
}

function logRequest(name: string, request: any) {
  eaveLogger.debug({ message: `${name}: request`, request });
}

function logResponse(name: string, response: RequestResponse) {
  let message: string;

  if (response.statusCode < 400) {
    message = `${name}: response`;
  } else {
    message = `${name}: API error`;
  }

  eaveLogger.debug({
    message,
    body: response.body,
    statusCode: response.statusCode,
    requestBody: response.request.body,
    requestUri: response.request.uri,
  });
}
