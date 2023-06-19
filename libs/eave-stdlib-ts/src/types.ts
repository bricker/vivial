export type JsonScalar =
  string |
  number |
  boolean |
  null |
  undefined;

export type JsonValue =
  JsonScalar |
  JsonValue[] |
  {[key:string]: JsonValue};

export type JsonObject = { [key: string]: JsonValue };

export type Pair<A, B> = { first: A, second: B };
