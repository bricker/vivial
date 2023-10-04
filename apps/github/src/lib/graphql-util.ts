import { Blob, Repository, Tree, validate } from "@octokit/graphql-schema";
import assert from "node:assert";
import { promises as fs } from "node:fs";
import GlobalCache from "../lib/cache.js";

/**
 * Asynchronously loads a GraphQL query from the cache or file system.
 * 
 * This function first checks if the query is available in the global cache. If it is, the cached query is returned.
 * If the query is not in the cache, it is read from the file system, validated, and then stored in the cache for future use.
 * 
 * @param {string} name - The name of the GraphQL query to load. This corresponds to the filename (without extension) in the `./src/graphql` directory.
 * 
 * @returns {Promise<string>} A promise that resolves to the full text of the GraphQL query.
 * 
 * @throws {Error} If the query fails validation, an error is thrown with a message detailing the validation errors.
 * 
 * @example
 * 
 * loadQuery('getUser').then(query => console.log(query)).catch(err => console.error(err));
 * 
 * @async
 */

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
  return fullQuery;
}

/**
 * Asynchronously prepends missing GraphQL fragments to a given query.
 *
 * This function scans the provided query for fragment usage, checks against a manifest of already included fragments,
 * and prepends any missing fragments to the query. It also updates the manifest with the newly included fragments.
 * If a fragment is not found in the GlobalCache, it reads the fragment from a file and then stores it in the cache.
 *
 * @param {string} query - The GraphQL query that may contain fragment references.
 * @param {Set<string>} [manifest] - An optional set of already included fragment names.
 *
 * @returns {Promise<string>} A promise that resolves to the updated query with all necessary fragments prepended.
 *
 * @example
 * ```typescript
 * const query = '...UserFragment';
 * const manifest = new Set(['UserFragment']);
 * const updatedQuery = await prependFragments(query, manifest);
 * ```
 *
 * @throws {Error} If the fragment file cannot be read.
 */
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
    let fragmentData = await GlobalCache.get(fragmentCacheKey);
    if (fragmentData === null) {
      fragmentData = await fs.readFile(
        `./src/graphql/fragments/${fragmentName}.graphql`,
        "utf-8",
      );
      await GlobalCache.set(fragmentCacheKey, fragmentData);
    }

    newQuery = `${fragmentData}\n\n${newQuery}`;
  }

  return prependFragments(newQuery, manifest);
}

```
/**
 * This function checks if a given object is of type 'Tree'.
 * 
 * @export
 * @function isTree
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @returns {boolean} Returns true if the object is of type 'Tree', false otherwise.
 */
```
export function isTree(
  obj: { __typename?: string } | undefined | null,
): obj is Tree {
  return obj?.__typename === "Tree";
}

```
/**
 * This function asserts whether the provided object is of type 'Tree'.
 * It throws an error if the object is not of type 'Tree'.
 *
 * @export
 * @function assertIsTree
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @throws {AssertionError} Throws an error if the object is not of type 'Tree'.
 * @returns {asserts obj is Tree} If the object is of type 'Tree', no error is thrown and the function returns.
 */
```
export function assertIsTree(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Tree {
  assert(isTree(obj), `expected Tree, got ${obj?.__typename}`);
}

/**
 * Checks if the given object is of type Blob.
 * 
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @returns {boolean} Returns true if the object is of type Blob, otherwise false.
 * 
 * @example
 * 
 * isBlob({ __typename: "Blob" }); // returns true
 * isBlob({ __typename: "NotBlob" }); // returns false
 * isBlob(null); // returns false
 * isBlob(undefined); // returns false
 */
export function isBlob(
  obj: { __typename?: string } | undefined | null,
): obj is Blob {
  return obj?.__typename === "Blob";
}

```
/**
 * This function asserts whether the provided object is of type Blob.
 * If the object is not a Blob, it throws an error with a message indicating the expected and actual types.
 *
 * @export
 * @function assertIsBlob
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked. It can be an object with an optional __typename property, undefined, or null.
 * @throws {AssertionError} Will throw an error if the object is not a Blob.
 */
```
export function assertIsBlob(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Blob {
  assert(isBlob(obj), `expected Blob, got ${obj?.__typename}`);
}

/**
 * Checks if the given object is a Repository.
 *
 * @param obj - The object to check. This can be an object with a `__typename` property, `undefined`, or `null`.
 * @returns A boolean indicating whether the object is a Repository. Returns `true` if the `__typename` property of the object is "Repository", `false` otherwise.
 *
 * @example
 * ```
 * const obj = { __typename: "Repository" };
 * isRepository(obj); // returns true
 * ```
 *
 * @example
 * ```
 * const obj = { __typename: "NotRepository" };
 * isRepository(obj); // returns false
 * ```
 *
 * @example
 * ```
 * const obj = null;
 * isRepository(obj); // returns false
 * ```
 */
export function isRepository(
  obj: { __typename?: string } | undefined | null,
): obj is Repository {
  return obj?.__typename === "Repository";
}

/**
 * Asserts whether the provided object is of type Repository.
 * 
 * @export
 * @function assertIsRepository
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @throws Will throw an error if the object is not of type Repository.
 * @returns {asserts obj is Repository} - Assertion result.
 */
export function assertIsRepository(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Repository {
  assert(isRepository(obj), `expected Repository, got ${obj?.__typename}`);
}
