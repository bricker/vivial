import ConnectClient, {
  RequestOpts,
} from "@eave-fyi/eave-stdlib-ts/src/connect/connect-client.js";
import { ADFRootNode } from "@eave-fyi/eave-stdlib-ts/src/connect/types/adf.js";
import { AtlassianProduct } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js";
import { AddOn } from "atlassian-connect-express";
import appConfig from "./config.js";
import { JiraComment, JiraUser } from "./types.js";

export default class JiraClient extends ConnectClient {
  static async getAuthedJiraClient({
    addon,
    teamId,
    clientKey,
  }: {
    addon: AddOn;
    teamId?: string;
    clientKey?: string;
  }): Promise<JiraClient> {
    const connectClient = await ConnectClient.getAuthedConnectClient({
      addon,
      product: AtlassianProduct.jira,
      origin: appConfig.eaveOrigin,
      teamId,
      clientKey,
    });

    return new JiraClient(connectClient);
  }

  async getUser({
    accountId,
  }: {
    accountId: string;
  }): Promise<JiraUser | undefined> {
    const request: RequestOpts = {
      url: "/rest/api/3/user",
      qs: {
        accountId,
      },
    };

    const response = await this.request("get", request);
    if (response.statusCode >= 400) {
      return undefined;
    }

    const user = <JiraUser>JSON.parse(response.body);
    return user;
  }

  /* https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post */
  async postComment({
    issueId,
    commentBody,
  }: {
    issueId: string;
    commentBody: ADFRootNode;
  }): Promise<JiraComment | undefined> {
    const request: RequestOpts = {
      url: `/rest/api/3/issue/${issueId}/comment`,
      json: true,
      body: { body: commentBody },
    };

    const response = await this.request("post", request);
    if (response.statusCode >= 400) {
      return undefined;
    }

    const comment = <JiraComment>response.body;
    return comment;
  }
}
