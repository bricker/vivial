import express, { Request, Response } from 'express';
import ace from 'atlassian-connect-express';
import helmet from 'helmet';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { loggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import { requireHeaders } from '@eave-fyi/eave-stdlib-ts/src/middleware/require-headers.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import headers from '@eave-fyi/eave-stdlib-ts/src/headers.js';
import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
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

// Include request parsers
app.use(express.json());
app.use(express.urlencoded({ extended: false })); // For GET requests

// Include atlassian-connect-express middleware
app.use(addon.middleware());

// We don't attach any routes to the root path / because all requests to this app are prefixed with /github
const rootRouter = express.Router();
app.use('/confluence', rootRouter);
rootRouter.use(requestIntegrity);
rootRouter.use(loggingMiddleware);
rootRouter.use(standardEndpointsRouter);

// webhooks
const webhookRouter = express.Router();
rootRouter.use('/events', webhookRouter);

const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.confluence, eaveOrigin: appConfig.eaveOrigin });
webhookRouter.use(lifecycleRouter);

webhookRouter.post('/', addon.authenticate(), async (req/* , res */) => {
  eaveLogger.info('received webhook event', { body: req.body, headers: req.headers });
});

// API
const internalApiRouter = express.Router();
rootRouter.use('/api', internalApiRouter);
internalApiRouter.use(requireHeaders(headers.EAVE_SIGNATURE_HEADER, headers.EAVE_TEAM_ID_HEADER, headers.EAVE_ORIGIN_HEADER));
internalApiRouter.use(originMiddleware);
internalApiRouter.use(signatureVerification(appConfig.eaveAppsBase));

internalApiRouter.post('/spaces/query', async (req: Request, res: Response) => {
  await getAvailableSpaces(req, res, addon);
});

internalApiRouter.post('/content/search', async (req: Request, res: Response) => {
  await searchContent(req, res, addon);
});

internalApiRouter.post('/content/create', async (req: Request, res: Response) => {
  await createContent(req, res, addon);
});

internalApiRouter.post('/content/update', async (req: Request, res: Response) => {
  await updateContent(req, res, addon);
});

internalApiRouter.post('/content/delete', async (req: Request, res: Response) => {
  await deleteContent(req, res, addon);
});

// internalApiRouter.all('/proxy', async (/* req: Request, res: Response */) => {
//   // TODO: Confluence API proxy?
// });

app.use(exceptionHandlingMiddleware);

const PORT = parseInt(process.env['PORT'] || '5400', 10);
app.listen(PORT, '0.0.0.0', () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    addon.register();
  }
});
