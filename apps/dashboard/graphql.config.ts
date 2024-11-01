import type { IGraphQLConfig } from "graphql-config";

const config: IGraphQLConfig = {
  // current gql schema specified by the core API (must be running core api + http-proxy locally!)
  schema: "https://api.eave.run:8080/graphql",
  documents: ["./eave/dashboard/js/graphql/**/*.graphql"],
};

export default config;
