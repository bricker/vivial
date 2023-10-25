import { EphemeralCache } from "@eave-fyi/eave-stdlib-ts/src/cache.js";
import {
  Blob,
  Commit,
  Repository,
  Tree,
  validate,
} from "@octokit/graphql-schema";
import assert from "node:assert";
import { promises as fs } from "node:fs";

const queryCache = new EphemeralCache();

export async function loadQuery(name: string): Promise<string> {
  const queryCacheKey = `query.${name}`;
  const cachedQuery = await queryCache.get(queryCacheKey);
  if (cachedQuery !== null) {
    return cachedQuery.toString();
  }

  const query = await fs.readFile(`./src/graphql/${name}.graphql`, "utf-8");
  const fullQuery = await prependFragments(query);

  const errors = await validate(fullQuery);
  if (errors.length > 0) {
    throw new Error(`GraphQL query ${name} is invalid: ${errors}`);
  }

  await queryCache.set(queryCacheKey, fullQuery);
  return fullQuery;
}

async function prependFragments(
  query: string,
  manifest?: Set<string>,
): Promise<string> {
  if (!manifest) {
    manifest = new Set<string>();
  }

  const fragmentMatches = Array.from(query.matchAll(/\.{3}(\w+?Fragment)/g));
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
    let fragmentData = await queryCache.get(fragmentCacheKey);
    if (fragmentData === null) {
      fragmentData = await fs.readFile(
        `./src/graphql/fragments/${fragmentName}.graphql`,
        "utf-8",
      );
      await queryCache.set(fragmentCacheKey, fragmentData);
    }

    newQuery = `${fragmentData}\n\n${newQuery}`;
  }

  return prependFragments(newQuery, manifest);
}

export function isTree(
  obj: { __typename?: string } | undefined | null,
): obj is Tree {
  return obj?.__typename === "Tree";
}

export function assertIsTree(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Tree {
  assert(isTree(obj), `expected Tree, got ${obj?.__typename}`);
}

export function isBlob(
  obj: { __typename?: string } | undefined | null,
): obj is Blob {
  return obj?.__typename === "Blob";
}

export function assertIsBlob(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Blob {
  assert(isBlob(obj), `expected Blob, got ${obj?.__typename}`);
}

export function isRepository(
  obj: { __typename?: string } | undefined | null,
): obj is Repository {
  return obj?.__typename === "Repository";
}

export function assertIsRepository(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Repository {
  assert(isRepository(obj), `expected Repository, got ${obj?.__typename}`);
}

export function isCommit(
  obj: { __typename?: string } | undefined | null,
): obj is Commit {
  return obj?.__typename === "Commit";
}

export function assertIsCommit(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Commit {
  assert(isCommit(obj), `expected Commit, got ${obj?.__typename}`);
}
