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
 * @param {string} name - The name of the GraphQL query to load. This corresponds to the filename (without extension) in the `./src/graphql/` directory.
 * 
 * @returns {Promise<string>} A promise that resolves to the loaded GraphQL query as a string.
 * 
 * @throws {Error} Throws an error if the loaded query is invalid according to the `validate` function.
 * 
 * @example
 * 
 * loadQuery('getUser').then(query => console.log(query)).catch(err => console.error(err));
 * 
 * @see {@link GlobalCache.get} for how queries are retrieved from the cache.
 * @see {@link GlobalCache.set} for how queries are stored in the cache.
 * @see {@link validate} for how queries are validated.
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
 * This asynchronous function prepends missing GraphQL fragments to a given query.
 * 
 * @param {string} query - The GraphQL query that may contain fragment references.
 * @param {Set<string>} [manifest] - An optional set of already included fragment names. If not provided, a new set will be created.
 * 
 * The function works by first checking if the manifest is provided. If not, a new Set is created.
 * It then finds all fragment references in the query and checks if they are included in the manifest.
 * If a fragment is not included, it is added to the manifest and its data is fetched from the GlobalCache.
 * If the fragment data is not in the cache, it is read from the file system and then added to the cache.
 * The fragment data is then prepended to the query.
 * This process is repeated until all fragments are included in the query.
 * 
 * @returns {Promise<string>} - Returns a promise that resolves with the updated query string.
 * 
 * @example
 * 
 * const query = `
 *   query {
 *     ...UserFragment
 *   }
 * `;
 * const manifest = new Set(['UserFragment']);
 * const updatedQuery = await prependFragments(query, manifest);
 * console.log(updatedQuery);
 * 
 * @throws {Error} - Throws an error if the fragment file cannot be read from the file system.
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
 * This function checks if the given object is of type 'Tree'.
 * 
 * @export
 * @function isTree
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked. It can be an object with an optional '__typename' property, or it can be 'undefined' or 'null'.
 * @returns {boolean} Returns 'true' if the object's '__typename' property is 'Tree', otherwise returns 'false'.
 */
```
export function isTree(
  obj: { __typename?: string } | undefined | null,
): obj is Tree {
  return obj?.__typename === "Tree";
}

/**
 * Asserts whether the provided object is of type 'Tree'.
 * 
 * @export
 * @function assertIsTree
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @throws Will throw an error if the object is not of type 'Tree'.
 * @returns {asserts obj is Tree} - Assertion result.
 */
export function assertIsTree(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Tree {
  assert(isTree(obj), `expected Tree, got ${obj?.__typename}`);
}

```
/**
 * This function checks if the provided object is of type Blob.
 * 
 * @export
 * @function isBlob
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked. It can be an object with an optional __typename property, undefined, or null.
 * @returns {boolean} Returns true if the object's __typename property is "Blob", otherwise returns false.
 */
```
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
 * @throws {AssertionError} Throws an error if the object is not of type Blob.
 * @returns {asserts obj is Blob} If the object is a Blob, the function completes without returning a value. Otherwise, it throws an error.
 */
```
export function assertIsBlob(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Blob {
  assert(isBlob(obj), `expected Blob, got ${obj?.__typename}`);
}

```
/**
 * This function checks if the provided object is a Repository.
 * 
 * @export
 * @function isRepository
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked. It can be an object with a __typename property, undefined, or null.
 * @returns {boolean} Returns true if the object is a Repository (i.e., if the __typename property of the object is "Repository"), otherwise returns false.
 */
```
export function isRepository(
  obj: { __typename?: string } | undefined | null,
): obj is Repository {
  return obj?.__typename === "Repository";
}

```
/**
 * This function asserts whether the provided object is of type Repository.
 * It throws an error if the object is not a Repository.
 *
 * @export
 * @function assertIsRepository
 * @param {({ __typename?: string } | undefined | null)} obj - The object to be checked.
 * @throws {AssertionError} Throws an error if the object is not a Repository.
 * @returns {asserts obj is Repository} If the object is a Repository, it doesn't return anything. It just confirms the type.
 */
```
export function assertIsRepository(
  obj: { __typename?: string } | undefined | null,
): asserts obj is Repository {
  assert(isRepository(obj), `expected Repository, got ${obj?.__typename}`);
}
