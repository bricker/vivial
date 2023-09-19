import { GAELifecycleRouter, StatusRouter } from "@eave-fyi/eave-stdlib-ts/src/api-util.js";
import { commonRequestMiddlewares, commonResponseMiddlewares, helmetMiddleware } from "@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js";
import express from "express";
import { InternalApiRouter } from "./api/routes.js";
import { WebhookRouter } from "./events/routes.js";
import { OfflineTaskRouter } from "./tasks/routes.js";
import { GITHUB_APP_API_MOUNT_PATH, GITHUB_APP_TASKS_MOUNT_PATH, GITHUB_APP_WEBHOOK_MOUNT_PATH } from "@eave-fyi/eave-stdlib-ts/src/github-api/operations/shared.js";

export const app = express();
app.use(helmetMiddleware());
app.use(commonRequestMiddlewares);
app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use(rootRouter);
rootRouter.use("/github/status", StatusRouter());
rootRouter.use(GITHUB_APP_WEBHOOK_MOUNT_PATH, WebhookRouter());
rootRouter.use(GITHUB_APP_API_MOUNT_PATH, InternalApiRouter());
rootRouter.use(GITHUB_APP_TASKS_MOUNT_PATH, OfflineTaskRouter());

app.use(commonResponseMiddlewares);
