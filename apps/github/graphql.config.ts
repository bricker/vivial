import type { IGraphQLConfig } from "graphql-config";

const config: IGraphQLConfig = {
  schema: "./node_modules/@octokit/graphql-schema/schema.graphql",
  documents: ["./src/graphql/**/*.graphql"],
};

export default config;
