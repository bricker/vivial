import { AddOn } from 'atlassian-connect-express';
import { Request } from 'express';
import ConnectClient, { RequestOpts } from '@eave-fyi/eave-stdlib-ts/src/connect/connect-client.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import appConfig from './config.js';
import { AtlassianDoc, Comment, User } from './types.js';

export default class JiraClient extends ConnectClient {
  static async getAuthedJiraClient({
    req,
    addon,
    teamId,
    clientKey,
  }: {
    req: Request,
    addon: AddOn,
    teamId?: string,
    clientKey?: string,
  }): Promise<JiraClient> {
    const connectClient = await ConnectClient.getAuthedConnectClient({
      req,
      addon,
      product: AtlassianProduct.jira,
      origin: appConfig.eaveOrigin,
      teamId,
      clientKey,
    });

    return new JiraClient(connectClient);
  }

  async getUser({ accountId }: { accountId: string }): Promise<User | undefined> {
    const request: RequestOpts = {
      url: '/rest/api/3/user',
      qs: {
        accountId,
      },
    };

    const response = await this.request('get', request);
    if (response.statusCode >= 400) {
      return undefined;
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
      return undefined;
    }

    const body = JSON.parse(response.body);
    const comment = <Comment>body;
    return comment;
  }
}
