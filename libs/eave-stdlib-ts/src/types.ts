export type JsonScalar = string | number | boolean | null | undefined;

export type JsonValue = JsonScalar | JsonValue[] | { [key: string]: JsonValue };

export type JsonObject = { [key: string]: JsonValue };

export type Pair<A, B> = { first: A; second: B };

export enum ExpressRoutingMethod {
  checkout = "checkout",
  copy = "copy",
  delete = "delete",
  get = "get",
  head = "head",
  lock = "lock",
  merge = "merge",
  mkactivity = "mkactivity",
  mkcol = "mkcol",
  move = "move",
  m_search = "m-search",
  notify = "notify",
  options = "options",
  patch = "patch",
  post = "post",
  purge = "purge",
  put = "put",
  report = "report",
  search = "search",
  subscribe = "subscribe",
  trace = "trace",
  unlock = "unlock",
  unsubscribe = "unsubscribe",
}

/**
 * Use for mixins
 * https://www.typescriptlang.org/docs/handbook/mixins.html
 */
export type Constructor = new (...args: any[]) => any;
export type GConstructor<T = NonNullable<unknown>> = new (...args: any[]) => T;

// Copied from node:crypto
// export type UUID = `${string}-${string}-${string}-${string}-${string}`;
export type UUID = string;