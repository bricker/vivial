import express, { NextFunction, Request, Response } from 'express';
import ace from 'atlassian-connect-express';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { requestLoggingMiddleware, responseLoggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import getCacheClient from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import { securityMiddlewares, genericMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import appConfig from './config.js';
import { internalApiMiddlewares, InternalApiRouter } from './api/routes.js';
import { WebhookRouter, webhookMiddlewares } from './events/routes.js';

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register('eave-api-store', EaveApiAdapter);

const app = express();
const addon = ace(app);
app.use(securityMiddlewares);
app.use(genericMiddlewares);
app.use('/confluence/api', internalApiMiddlewares());
app.use('/confluence/events', webhookMiddlewares({ addon }));

app.get('/_ah/warmup', async (req: Request, res: Response) => {
  await getCacheClient; // Initializes a client and connects to Redis
  res.status(200);
});

const rootRouter = express.Router();
app.use('/confluence', rootRouter);
rootRouter.use(standardEndpointsRouter);

// webhooks
const webhookRouter = WebhookRouter({ addon });
rootRouter.use('/events', webhookRouter);

const internalApiRouter = InternalApiRouter({ addon });
rootRouter.use('/api', internalApiRouter);

app.use(responseLoggingMiddleware);
app.use(exceptionHandlingMiddleware);

const PORT = parseInt(process.env['PORT'] || '5400', 10);
const server = app.listen(PORT, '0.0.0.0', () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    addon.register();
  }
});

const gracefulShutdownHandler = () => {
  getCacheClient
    .then((client) => client.quit())
    .then(() => { eaveLogger.info('redis connection closed.'); });

  server.close(() => {
    eaveLogger.info('HTTP server closed');
  });
};

process.on('SIGTERM', gracefulShutdownHandler);
process.on('SIGINT', gracefulShutdownHandler);
