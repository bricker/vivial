import express from 'express';
import { commonRequestMiddlewares, commonResponseMiddlewares, helmetMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { GAELifecycleRouter, StatusRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { TaskQueueRouter, WebhookRouter } from './events/routes.js';
import { InternalApiRouter } from './api/routes.js';

export const app = express();
app.use(helmetMiddleware());
app.use(commonRequestMiddlewares);
app.use(GAELifecycleRouter());

app.use('/_tasks', TaskQueueRouter());

const rootRouter = express.Router();
app.use('/github', rootRouter);

rootRouter.use(StatusRouter());
rootRouter.use('/events', WebhookRouter());
rootRouter.use('/api', InternalApiRouter());

app.use(commonResponseMiddlewares);
