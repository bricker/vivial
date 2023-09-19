import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GITHUB_APP_API_MOUNT_PATH, GithubAppEndpointConfiguration } from "./shared.js";

export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export class GetGithubUrlContentOperation {
  static config = new GithubAppEndpointConfiguration({
    mountPath: GITHUB_APP_API_MOUNT_PATH,
    subPath: "/content",
    authRequired: false,
  })

  static async perform(args: RequestArgsTeamId & {
    input: GetGithubUrlContentRequestBody,
  }): Promise<GetGithubUrlContentResponseBody> {
    const resp = await makeRequest({
      url: this.config.url,
      ...args,
    });
    const responseData = <GetGithubUrlContentResponseBody>(await resp.json());
    return responseData;
  }
}