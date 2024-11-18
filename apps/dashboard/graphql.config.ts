import type { IGraphQLConfig } from "graphql-config";
import sharedGraphqlConfig from "../../develop/shared/graphql.config";

const config: IGraphQLConfig = {
  ...sharedGraphqlConfig,
  documents: ["./eave/dashboard/**/*.graphql"],
};

export default config;
