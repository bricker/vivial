import { schema } from "@eave-fyi/develop/graphql.config";
import type { IGraphQLConfig } from "graphql-config";

const config: IGraphQLConfig = {
  projects: {
    dashboard: {
      schema,
      documents: "./apps/dashboard/**/*.graphql",
    },
    core: {
      schema,
      documents: "./apps/core/**/*.graphql",
    },
  },
};

export default config;
