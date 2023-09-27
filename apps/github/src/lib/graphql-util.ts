import { Issue, ProjectV2Item, Query, validate } from "@octokit/graphql-schema";
import { promises as fs } from "node:fs";
import GlobalCache from "../lib/cache.js";
import { GitHubOperationsContext } from "../types.js";

export async function loadQuery(name: string): Promise<string> {
  const queryCacheKey = `query.${name}`;
  const cachedQuery = await GlobalCache.get(queryCacheKey);
  if (cachedQuery !== null) {
    return cachedQuery.toString();
  }

  const query = await fs.readFile(`./src/graphql/${name}.graphql`, "utf-8");
  const fullQuery = await prependFragments(query);

  const errors = await validate(fullQuery);
  if (errors.length > 0) {
    throw new Error(`GraphQL query ${name} is invalid: ${errors}`);
  }

  await GlobalCache.set(queryCacheKey, fullQuery);
  return query;
}

async function prependFragments(query: string, manifest?: Set<string>): Promise<string> {
  if (!manifest) {
    manifest = new Set<string>();
  }

  const fragmentMatches = Array.from(query.matchAll(/\.{3}(.+?)Fragment/g));
  const missingFragments = fragmentMatches.filter((m) => {
    return !manifest!.has(m[1]!);
  }).map((f) => f[1]!);

  if (missingFragments.length === 0) {
    return query;
  }

  let newQuery = query;

  for (const fragmentName of missingFragments) {
    manifest.add(fragmentName);
    const fragmentCacheKey = `fragment.${fragmentName}`;
    let fragmentData = await GlobalCache.get(fragmentCacheKey);
    if (fragmentData === null) {
      fragmentData = await fs.readFile(`./src/graphql/fragments/_${fragmentName}.graphql`, "utf-8");
      await GlobalCache.set(fragmentCacheKey, fragmentData);
    }

    newQuery = `${fragmentData}\n\n${newQuery}`;
  }

  return prependFragments(newQuery, manifest);
}

export async function getProjectV2ItemFieldValue(itemNodeId: string, fieldName: string, context: GitHubOperationsContext): Promise<ProjectV2Item> {
  const query = await loadQuery("getProjectV2ItemFieldValue");
  const variables = {
    itemNodeId,
    fieldName,
  };

  const response = await context.octokit.graphql<{ node: Query["node"] }>(query, variables);
  const projectV2Item = <ProjectV2Item>response.node!;
  return projectV2Item;
}

// export async function getLabel(labelName: string, context: GitHubOperationsContext): Promise<Label> {
//   return GlobalCache.getOrSet(`github.label.${labelName}`, (6 * 60 * 60 * 1000), async () => {
//     const query = await loadQuery('getLabel');
//     const variables = {
//       ...Constants.REPO_VARIABLES,
//       labelName,
//     };

//     const response = await context.octokit.graphql<{ repository: Query['repository'] }>(query, variables);
//     return response.repository!.label!;
//   });
// }

// export async function getProjectV2Field(fieldName: string, context: GitHubOperationsContext): Promise<ProjectV2FieldConfiguration> {
//   return GlobalCache.getOrSet(`github.projectV2Field.${fieldName}`, (6 * 60 * 60 * 1000), async (): Promise<ProjectV2FieldConfiguration> => {
//     const query = await loadQuery('getProjectV2Field');
//     const variables = {
//       ...Constants.REPO_VARIABLES,
//       projectNumber: Constants.PROJECT_NUMBER,
//       fieldName: 'Issue Type',
//     };

//     const response = await context.octokit.graphql<{ repository: Query['repository'] }>(query, variables);
//     return response.repository!.projectV2!.field!;
//   });
// }

export async function getIssueByNodeId(nodeId: string, context: GitHubOperationsContext): Promise<Issue> {
  const query = await loadQuery("getIssueByNodeId");
  const variables = {
    nodeId,
  };

  const response = await context.octokit.graphql<{ node: Query["node"] }>(query, variables);
  const item = <Issue>response.node;
  return item;
}
