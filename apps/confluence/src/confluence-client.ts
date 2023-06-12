import { ConfluenceContentBody, ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluenceContentType, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResultWithBody, ConfluenceSpace, ConfluenceSpaceContentDepth, ConfluenceSpaceStatus, ConfluenceSpaceType, SystemInfoEntity } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { AddOn, HostClient } from 'atlassian-connect-express';
import { RequestResponse } from 'request';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { cleanDocument } from './api/util.js';
import { Request } from 'express';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import appConfig from './config.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { promisify } from 'util';

export default class ConfluenceClient {
  static async getAuthedConnectClient(req: Request, addon: AddOn): Promise<ConfluenceClient> {
    const teamId = req.header(headers.EAVE_TEAM_ID_HEADER)!; // presence already validated

    const connectIntegrationResponse = await queryConnectInstallation({
      origin: appConfig.eaveOrigin,
      input: {
        connect_integration: {
          product: AtlassianProduct.confluence,
          team_id: teamId,
        },
      },
    });

    return this.getAuthedConnectClientForClientKey(connectIntegrationResponse.connect_integration.client_key, addon);
  }

  private static getAuthedConnectClientForClientKey(clientKey: string, addon: AddOn): ConfluenceClient {
    const client = addon.httpClient({ clientKey });
    client.get = promisify<any, any>(client.get);
    client.post = promisify<any, any>(client.post);
    client.put = promisify<any, any>(client.put);
    client.del = promisify<any, any>(client.del);
    client.head = promisify<any, any>(client.head);
    client.patch = promisify<any, any>(client.patch);

    return new ConfluenceClient(client);
  }

  client: HostClient;

  constructor(client: HostClient) {
    this.client = client;
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-spacekey-get
  */
  async getSpaceByKey({ spaceKey }: { spaceKey: string }): Promise<ConfluenceSpace | null> {
    const request = {
      url: `/rest/api/space/${spaceKey}`,
      qs: {
        expand: 'homepage',
      },
    };
    this.logRequest('getSpaceByKey', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getSpaceByKey', response);
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
  async getPageByTitle({ space, title }: { space: ConfluenceSpace, title: string }): Promise<ConfluencePage | null> {
    const request = {
      url: '/rest/api/content',
      qs: {
        type: 'page',
        space: space.key,
        title,
      },
    };
    this.logRequest('getPageByTitle', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getPageByTitle', response);
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
  async getPageById({ pageId }: { pageId: string }): Promise<ConfluencePage | null> {
    const request = {
      url: `/rest/api/content/${pageId}`,
    };
    this.logRequest('getPageById', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getPageById', response);
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
  async getPageChildren({ pageId }: { pageId: string | number }): Promise<ConfluencePage[]> {
    const request = {
      url: `/rest/api/content/${pageId}/child/${ConfluenceContentType.page}`,
      qs: {
        limit: 100, // TODO: Pagination
      },
    };
    this.logRequest('getPageChildren', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getPageChildren', response);
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
  async getSpaceRootPage({ space }: { space: ConfluenceSpace }): Promise<ConfluencePage | null> {
    const request = {
      url: `/rest/api/space/${space.key}/content/${ConfluenceContentType.page}`,
      qs: {
        depth: ConfluenceSpaceContentDepth.root,
      },
    };
    this.logRequest('getSpaceRootPage', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getSpaceRootPage', response);
    if (response.statusCode >= 400) {
      return null;
    }

    const body = JSON.parse(response.body);
    const root = <ConfluencePage[]>body.results;

    if (root && root[0]) {
      return <ConfluencePage>root[0];
    } else {
      return null;
    }
  }

  /* https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-page/#api-pages-post */
  async createPage({ space, body, title, parentId }: { space: ConfluenceSpace, title: string, body: string, parentId?: string }): Promise<ConfluencePage | null> {
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

    this.logRequest('createPage', request);

    const response: RequestResponse = await this.client.post(request);
    this.logResponse('createPage', response);
    if (response.statusCode >= 400) {
      return null;
    }

    const page = <ConfluencePage>response.body;
    return page;
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content/#api-wiki-rest-api-content-archive-post
  */
  async archivePage({ contentId }: { contentId: string }) {
    const request = {
      url: '/rest/api/content/archive',
      json: true,
      body: {
        pages: [
          { id: contentId },
        ],
      },
    };
    this.logRequest('archivePage', request);
    const response: RequestResponse = await this.client.post(request);
    this.logResponse('archivePage', response);
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
  */
  async getSpaces(): Promise<ConfluenceSpace[]> {
    const request = {
      url: '/rest/api/space',
      qs: {
        status: ConfluenceSpaceStatus.current,
        type: ConfluenceSpaceType.global,
      },
    };
    this.logRequest('getSpaces', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('getSpaces', response);
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
  async search({ cql, cqlcontext }: { cql: string, cqlcontext?: {[key: string]: any} }): Promise<ConfluenceSearchResultWithBody[]> {
    const request = {
      url: '/rest/api/content/search',
      qs: {
        cql,
        cqlcontext: cqlcontext ? JSON.stringify(cqlcontext) : undefined,
        expand: ['body.storage'],
      },
    };
    this.logRequest('search', request);

    const response: RequestResponse = await this.client.get(request);
    this.logResponse('search', response);
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
  async updatePage({ page, body }: { page: ConfluencePage, body: string }): Promise<ConfluencePage | null> {
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
    this.logRequest('updatePage', request);

    const response: RequestResponse = await this.client.put(request);
    this.logResponse('updatePage', response);
    if (response.statusCode >= 400) {
      return null;
    }

    return <ConfluencePage>response.body;
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-settings/#api-wiki-rest-api-settings-systeminfo-get
  */
  async getSystemInfo(): Promise<SystemInfoEntity | null> {
    const request = {
      url: '/rest/api/settings/systemInfo',
    };
    this.logRequest('getSystemInfo', request);

    const response: RequestResponse = await client.put(request);
    this.logResponse('getSystemInfo', response);
    if (response.statusCode >= 400) {
      return null;
    }

    const body = JSON.parse(response.body);
    return <SystemInfoEntity>body;
  }

  private logRequest(name: string, request: any) {
    eaveLogger.debug({ message: `${name}: request`, request });
  }

  private logResponse(name: string, response: RequestResponse) {
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
}