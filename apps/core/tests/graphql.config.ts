import type { IGraphQLConfig } from "graphql-config";
import sharedGraphqlConfig from "../../../develop/shared/graphql.config.js";sharedGraphqlConfig

const config: IGraphQLConfig = {
  ...sharedGraphqlConfig,
  documents: ["./core/**/*.graphql"],
};

export default config;
