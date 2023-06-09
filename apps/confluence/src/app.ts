import express, { NextFunction, Request, Response } from 'express';
import ace from 'atlassian-connect-express';
import helmet from 'helmet';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { loggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import { requireHeaders } from '@eave-fyi/eave-stdlib-ts/src/middleware/require-headers.js';
import { bodyParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import getCacheClient from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import appConfig from './config.js';
import getAvailableSpaces from './api/get-available-spaces.js';
import searchContent from './api/search-content.js';
import createContent from './api/create-content.js';
import deleteContent from './api/delete-content.js';
import updateContent from './api/update-content.js';

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register('eave-api-store', EaveApiAdapter);

const app = express();
const addon = ace(app);

// addon.on('host_settings_saved', async (clientKey, settings) => {
//   const client = await getAuthedConnectClientForClientKey(clientKey, addon);
// });

// Atlassian security policy requirements
// http://go.atlassian.com/security-requirements-for-cloud-apps
// HSTS must be enabled with a minimum age of at least one year
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: false,
}));
app.use(helmet.referrerPolicy({
  policy: ['origin'],
}));

app.use(helmet.xPoweredBy);

// Atlassian security policy requirements
// http://go.atlassian.com/security-requirements-for-cloud-apps
app.use((req, res, next) => {
  res.setHeader('Surrogate-Control', 'no-store');
  res.setHeader(
    'Cache-Control',
    'no-store, no-cache, must-revalidate, proxy-revalidate',
  );
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');

  next();
});

const rootRouter = express.Router();
app.get('/_ah/warmup', async (req: Request, res: Response) => {
  await getCacheClient; // Initializes a client and connects to Redis
  res.status(200);
});

app.use('/confluence', rootRouter);
rootRouter.use(requestIntegrity);
rootRouter.use(loggingMiddleware);
rootRouter.use(standardEndpointsRouter);

// webhooks
const webhookRouter = express.Router();
rootRouter.use('/events', webhookRouter);
webhookRouter.use(express.json());
webhookRouter.use(addon.middleware());

const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.confluence, eaveOrigin: appConfig.eaveOrigin });
webhookRouter.use(lifecycleRouter);

webhookRouter.post('/', addon.authenticate(), async (req/* , res */) => {
  eaveLogger.info('received webhook event', { body: req.body, headers: req.headers });
});

// API
const internalApiRouter = express.Router();
rootRouter.use('/api', internalApiRouter);

// raw is used here so that we have access to the raw body for signature verification.
internalApiRouter.use(express.raw({ type: 'application/json' }));
internalApiRouter.use(requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER));
internalApiRouter.use(originMiddleware);
internalApiRouter.use(signatureVerification(appConfig.eaveAppsBase));
internalApiRouter.use(bodyParser); // This goes _after_ signature verification, so that signature verification has access to the raw body.

internalApiRouter.post('/spaces/query', (req: Request, res: Response, next: NextFunction) => {
  getAvailableSpaces(req, res, addon).catch(next);
});

internalApiRouter.post('/content/search', (req: Request, res: Response, next: NextFunction) => {
  searchContent(req, res, addon).catch(next);
});

internalApiRouter.post('/content/create', (req: Request, res: Response, next: NextFunction) => {
  createContent(req, res, addon).catch(next);
});

internalApiRouter.post('/content/update', (req: Request, res: Response, next: NextFunction) => {
  updateContent(req, res, addon).catch(next);
});

internalApiRouter.post('/content/delete', (req: Request, res: Response, next: NextFunction) => {
  deleteContent(req, res, addon).catch(next);
});

// internalApiRouter.all('/proxy', async (/* req: Request, res: Response */) => {
//   // TODO: Confluence API proxy?
// });

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
