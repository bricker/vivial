export declare type JsonValue =
  string |
  number |
  null |
  string[] |
  number[] |
  null[] |
  { [key: string]: JsonValue } |
  { [key: string]: JsonValue }[];

export type Pair<A, B> = { first: A, second: B };