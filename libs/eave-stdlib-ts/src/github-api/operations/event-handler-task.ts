import { RequestArgsTeamId, makeRequest } from "../../requests.js";
import { GithubRepoInput } from "../models.js";
import { GithubAppEndpointConfiguration } from "./shared.js";

export const config = new GithubAppEndpointConfiguration({
  path: "/_/github/events",
  authRequired: false,
})
