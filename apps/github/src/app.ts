import express from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { applyCommonRequestMiddlewares, applyCommonResponseMiddlewares, applyInternalApiMiddlewares, helmetMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { GAELifecycleRouter, StatusRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { WebhookRouter, applyWebhookMiddlewares } from './events/routes.js';
import { InternalApiRouter } from './api/routes.js';

export const app = express();
app.use(helmetMiddleware());
applyCommonRequestMiddlewares({ app });
applyInternalApiMiddlewares({ app, path: '/github/api' });
applyWebhookMiddlewares({ app, path: '/github/events' });

app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use('/github', rootRouter);
rootRouter.use(StatusRouter());
rootRouter.use('/events', WebhookRouter());
rootRouter.use('/api', InternalApiRouter());

applyCommonResponseMiddlewares({ app });
