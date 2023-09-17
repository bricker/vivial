import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export const config = new GithubAppEndpointConfiguration({
  path: "/_/github/run-api-documentation",
  authRequired: false,
})

export type RunApiDocumentationTaskRequestBody = {
  repo: GithubRepoInput;
}

export async function runApiDocumentationTask(args: RequestArgsTeamId & {
  input: RunApiDocumentationTaskRequestBody,
}): Promise<void> {
  await makeRequest({
    url: config.url,
    ...args,
  });
}
