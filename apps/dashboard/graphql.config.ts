import type { IGraphQLConfig } from "graphql-config";
import sharedGraphqlConfig from "@eave-fyi/develop/graphql.config";

const config: IGraphQLConfig = {
  ...sharedGraphqlConfig,
  documents: ["./eave/dashboard/**/*.graphql"],
};

export default config;
