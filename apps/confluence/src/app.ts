import express from "express";
import ace from "atlassian-connect-express";
import { atlassianSecurityPolicyMiddlewares } from "@eave-fyi/eave-stdlib-ts/src/connect/security-policy-middlewares.js";
import { StatusRouter, addGAELifecycleRoutes } from "@eave-fyi/eave-stdlib-ts/src/api-util.js";
import EaveApiAdapter from "@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js";
import { helmetMiddleware, commonRequestMiddlewares, commonResponseMiddlewares } from "@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js";
import { InternalApiRouter } from "./api/routes.js";
import { WebhookRouter } from "./events/routes.js";
import eaveConfig from "./config.js";

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register("eave-api-store", EaveApiAdapter);

export const app = express();
export const addon = ace(app, {
  config: {
    descriptorTransformer: (descriptor, config): any => {
      if (config.environment() === "production") {
        descriptor.baseUrl = `${eaveConfig.eavePublicAppsBase}/confluence`;
      }
      return descriptor;
    },
  },
});

app.use(helmetMiddleware());
app.use(atlassianSecurityPolicyMiddlewares);
app.use(commonRequestMiddlewares);
addGAELifecycleRoutes({ router: app });

const rootRouter = express.Router();
app.use("/confluence", rootRouter);

rootRouter.use("/status", StatusRouter());
rootRouter.use("/events", WebhookRouter({ addon }));
rootRouter.use("/api", InternalApiRouter({ addon }));

app.use(commonResponseMiddlewares);
