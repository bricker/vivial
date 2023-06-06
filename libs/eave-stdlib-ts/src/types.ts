export type JsonObject = { [key: string]: any };

export type JsonValue =
  string |
  number |
  null |
  string[] |
  number[] |
  null[] |
  JsonObject |
  JsonObject[];

export type Pair<A, B> = { first: A, second: B };
