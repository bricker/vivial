import type { IGraphQLConfig } from "graphql-config";
import sharedGraphqlConfig from "../../../develop/javascript/graphql.config";

const config: IGraphQLConfig = {
  ...sharedGraphqlConfig,
  documents: ["./core/**/*.graphql"],
};

export default config;
