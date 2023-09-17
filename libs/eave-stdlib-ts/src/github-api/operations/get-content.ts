import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export const config = new GithubAppEndpointConfiguration({
  path: "/github/api/content",
  authRequired: false,
})

export type GetGithubUrlContentRequestBody = {
  url: string;
}

export type GetGithubUrlContentResponseBody = {
  content: string | null;
}

export async function getGithubUrlContent(args: RequestArgsTeamId & {
  input: GetGithubUrlContentRequestBody,
}): Promise<GetGithubUrlContentResponseBody> {
  const resp = await makeRequest({
    url: config.url,
    ...args,
  });
  const responseData = <GetGithubUrlContentResponseBody>(await resp.json());
  return responseData;
}
