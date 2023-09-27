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

async function prependFragments(
  query: string,
  manifest?: Set<string>,
): Promise<string> {
  if (!manifest) {
    manifest = new Set<string>();
  }

  const fragmentMatches = Array.from(query.matchAll(/\.{3}(.+?)Fragment/g));
  const missingFragments = fragmentMatches
    .filter((m) => {
      return !manifest!.has(m[1]!);
    })
    .map((f) => f[1]!);

  if (missingFragments.length === 0) {
    return query;
  }

  let newQuery = query;

  for (const fragmentName of missingFragments) {
    manifest.add(fragmentName);
    const fragmentCacheKey = `fragment.${fragmentName}`;
    let fragmentData = await GlobalCache.get(fragmentCacheKey);
    if (fragmentData === null) {
      fragmentData = await fs.readFile(
        `./src/graphql/fragments/_${fragmentName}.graphql`,
        "utf-8",
      );
      await GlobalCache.set(fragmentCacheKey, fragmentData);
    }

    newQuery = `${fragmentData}\n\n${newQuery}`;
  }

  return prependFragments(newQuery, manifest);
}
