import express from 'express';
import { GAELifecycleRouter, StatusRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { helmetMiddleware, applyCommonRequestMiddlewares, applyCommonResponseMiddlewares, applyInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { InternalApiRouter } from './api/routes.js';

export const app = express();

app.use(helmetMiddleware());
applyCommonRequestMiddlewares({ app });
applyInternalApiMiddlewares({ path: '/{{service_name}}/api', app });

app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use('/{{service_name}}', rootRouter);

rootRouter.use(StatusRouter());
rootRouter.use('/api', InternalApiRouter();

applyCommonResponseMiddlewares({ app });
