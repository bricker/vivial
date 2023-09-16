import express from 'express';
import { commonRequestMiddlewares, commonResponseMiddlewares, helmetMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { GAELifecycleRouter, StatusRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { WebhookOfflineTaskRouter, WebhookRouter } from './events/routes.js';
import { InternalApiRouter } from './api/routes.js';
import { OfflineTaskRouter } from './tasks/routes.js';

export const app = express();
app.use(helmetMiddleware());
app.use(commonRequestMiddlewares);
app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use('/github', rootRouter);
rootRouter.use(StatusRouter());
rootRouter.use(WebhookRouter());
rootRouter.use(InternalApiRouter());

// This isn't mounted on the `rootRouter` because it isn't namespaced under `/github` (and therefore not accessible through the load balancer)
const taskQueueRouter = express.Router();
app.use('/_/github', taskQueueRouter);
taskQueueRouter.use(WebhookOfflineTaskRouter());
taskQueueRouter.use(OfflineTaskRouter());

app.use(commonResponseMiddlewares);
