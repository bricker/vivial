import type { IGraphQLConfig } from "graphql-config";

// current gql schema specified by the core API
export const schema = process.env["GRAPHQL_SCHEMA"] || "http://api.eave.run:8080/graphql";

const config: IGraphQLConfig = {
  schema,
};

export default config;
