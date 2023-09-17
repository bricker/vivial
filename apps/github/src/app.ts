import { GAELifecycleRouter, StatusRouter } from "@eave-fyi/eave-stdlib-ts/src/api-util.js";
import { commonRequestMiddlewares, commonResponseMiddlewares, helmetMiddleware } from "@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js";
import express from "express";
import { InternalApiRouter } from "./api/routes.js";
import { WebhookOfflineTaskRouter, WebhookRouter } from "./events/routes.js";
import { OfflineTaskRouter } from "./tasks/routes.js";

export const app = express();
app.use(helmetMiddleware());
app.use(commonRequestMiddlewares);
app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use(rootRouter);
rootRouter.use("/github", StatusRouter());
rootRouter.use(WebhookRouter());
rootRouter.use(InternalApiRouter());
rootRouter.use(WebhookOfflineTaskRouter());
rootRouter.use(OfflineTaskRouter());

app.use(commonResponseMiddlewares);
