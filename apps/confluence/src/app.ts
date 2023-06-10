import express, { Request, Response } from 'express';
import ace from 'atlassian-connect-express';
import { applyAtlassianSecurityPolicyMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/connect/security-policy-middlewares.js';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { GAELifecycleRouter, StatusRouter, applyShutdownHandlers } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import getCacheClient from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import { helmetMiddleware, applyCommonRequestMiddlewares, applyCommonResponseMiddlewares, applyInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import appConfig from './config.js';
import { InternalApiRouter } from './api/routes.js';
import { WebhookRouter, applyWebhookMiddlewares } from './events/routes.js';

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register('eave-api-store', EaveApiAdapter);

const app = express();
const addon = ace(app);
app.use(helmetMiddleware());
applyAtlassianSecurityPolicyMiddlewares({ app });
applyCommonRequestMiddlewares({ app });
applyInternalApiMiddlewares({ path: '/confluence/api', app });
applyWebhookMiddlewares({ app, addon, path: '/confluence/events' });

app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use('/confluence', rootRouter);

rootRouter.use(StatusRouter());
rootRouter.use('/events', WebhookRouter({ addon }));
rootRouter.use('/api', InternalApiRouter({ addon }));

applyCommonResponseMiddlewares({ app });

const PORT = parseInt(process.env['PORT'] || '5400', 10);
const server = app.listen(PORT, '0.0.0.0', () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    addon.register();
  }
});

applyShutdownHandlers({ server });
