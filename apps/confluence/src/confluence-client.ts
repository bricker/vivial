import { ConfluenceContentBody, ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluenceContentType, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResultWithBody, ConfluenceSpace, ConfluenceSpaceContentDepth, ConfluenceSpaceStatus, ConfluenceSpaceType, SystemInfoEntity } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { AddOn } from 'atlassian-connect-express';
import { Request } from 'express';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import ConnectClient, { RequestOpts } from '@eave-fyi/eave-stdlib-ts/src/connect/connect-client.js';
import appConfig from './config.js';
import { cleanDocument } from './api/util.js';

export default class ConfluenceClient extends ConnectClient {
  static async getAuthedConfluenceClient({
    req,
    addon,
    teamId,
    clientKey,
  }: {
    req: Request,
    addon: AddOn,
    teamId?: string,
    clientKey?: string,
  }): Promise<ConfluenceClient> {
    const connectClient = await ConnectClient.getAuthedConnectClient({
      req,
      addon,
      product: AtlassianProduct.confluence,
      origin: appConfig.eaveOrigin,
      teamId,
      clientKey,
    });

    return new ConfluenceClient(connectClient);
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/#api-wiki-rest-api-space-spacekey-get
  */
  async getSpaceByKey({ spaceKey }: { spaceKey: string }): Promise<ConfluenceSpace | null> {
    const request: RequestOpts = {
      url: `/rest/api/space/${spaceKey}`,
      qs: {
        expand: 'homepage',
      },
    };

    const response = await this.request('get', request);
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
    const request: RequestOpts = {
      url: '/rest/api/content',
      qs: {
        type: 'page',
        space: space.key,
        title,
      },
    };

    const response = await this.request('get', request);
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
    const request: RequestOpts = {
      url: `/rest/api/content/${pageId}`,
      qs: {
        expand: 'body.storage,version',
      },
    };

    const response = await this.request('get', request);
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
    const request: RequestOpts = {
      url: `/rest/api/content/${pageId}/child/${ConfluenceContentType.page}`,
      qs: {
        limit: 100, // TODO: Pagination
      },
    };

    const response = await this.request('get', request);
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
    const request: RequestOpts = {
      url: `/rest/api/space/${space.key}/content/${ConfluenceContentType.page}`,
      qs: {
        depth: ConfluenceSpaceContentDepth.root,
      },
    };

    const response = await this.request('get', request);
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

    const request: RequestOpts = {
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

    const response = await this.request('post', request);
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
    const request: RequestOpts = {
      url: '/rest/api/content/archive',
      json: true,
      body: {
        pages: [
          { id: contentId },
        ],
      },
    };
    await this.request('post', request);
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v2/api-group-space/#api-spaces-get
  */
  async getSpaces(): Promise<ConfluenceSpace[]> {
    const request: RequestOpts = {
      url: '/rest/api/space',
      qs: {
        status: ConfluenceSpaceStatus.current,
        type: ConfluenceSpaceType.global,
      },
    };

    const response = await this.request('get', request);
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
    const request: RequestOpts = {
      url: '/rest/api/content/search',
      qs: {
        cql,
        cqlcontext: cqlcontext ? JSON.stringify(cqlcontext) : undefined,
        expand: 'body.storage,version',
      },
    };

    const response = await this.request('get', request);
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

    const request: RequestOpts = {
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

    const response = await this.request('put', request);
    if (response.statusCode >= 400) {
      return null;
    }

    return <ConfluencePage>response.body;
  }

  /*
  https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-settings/#api-wiki-rest-api-settings-systeminfo-get
  */
  async getSystemInfo(): Promise<SystemInfoEntity | null> {
    const request: RequestOpts = {
      url: '/rest/api/settings/systemInfo',
    };

    const response = await this.request('put', request);
    if (response.statusCode >= 400) {
      return null;
    }

    const body = JSON.parse(response.body);
    return <SystemInfoEntity>body;
  }
}
