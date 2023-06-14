import { ConfluenceContentBody, ConfluenceContentBodyRepresentation, ConfluenceContentStatus, ConfluenceContentType, ConfluencePage, ConfluencePageBodyWrite, ConfluenceSearchResultWithBody, ConfluenceSpace, ConfluenceSpaceContentDepth, ConfluenceSpaceStatus, ConfluenceSpaceType, SystemInfoEntity } from '@eave-fyi/eave-stdlib-ts/src/confluence-api/models.js';
import { AddOn, HostClient } from 'atlassian-connect-express';
import { CoreOptions, RequestResponse, UrlOptions } from 'request';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { Request } from 'express';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import ConnectClient, { RequestOpts } from '@eave-fyi/eave-stdlib-ts/src/connect/connect-client.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import { promisify } from 'util';
import appConfig from './config.js';
import { AtlassianDoc, Comment, ContentType, User } from './types.js';

export default class JiraClient extends ConnectClient {
  static async getAuthedJiraClient(req: Request, addon: AddOn): Promise<JiraClient> {
    const connectClient = await ConnectClient.getAuthedConnectClient({
      req,
      addon,
      product: AtlassianProduct.jira,
      origin: appConfig.eaveOrigin,
    });

    return new JiraClient(connectClient);
  }

  async getUser({ accountId }: { accountId: string }): Promise<User | undefined> {
    const request: RequestOpts = {
      url: '/rest/api/3/user',
      qs: {
        accountId
      },
    }

    const response = await this.request('get', request);
    if (response.statusCode >= 400) {
      return;
    }

    const body = JSON.parse(response.body);
    const user = <User>body;
    return user;
  }

  async postComment({ issueId, commentBody }: { issueId: string, commentBody: AtlassianDoc }): Promise<Comment | undefined> {
    const request: RequestOpts = {
      url: `/rest/api/3/issue/${issueId}/comment`,
      json: true,
      body: {
        body: commentBody,
      },
    };

    const response = await this.request('post', request);
    if (response.statusCode >= 400) {
      return;
    }

    const body = JSON.parse(response.body);
    const comment = <Comment>body;
    return comment;
  }
}
