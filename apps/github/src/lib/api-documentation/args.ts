import { GithubRepo } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/github-repos.js";
import { GitHubOperationsContext } from "../../types.js";
import { ExpressParsingUtility } from "@eave-fyi/eave-stdlib-ts/src/api-documenting/express-parsing-utility.js";
import { Repository } from "@octokit/graphql-schema";

export type ExpressAPIDocumentorArgs = GitHubOperationsContext & { githubRepo: Repository, eaveRepo: GithubRepo, parser: ExpressParsingUtility };
