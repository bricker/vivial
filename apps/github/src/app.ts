import express from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { loggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { setOrigin } from '@eave-fyi/eave-stdlib-ts/src/lib/requests.js';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import dispatch from './dispatch.js';
import { getSummary } from './requests/content.js';
import { subscribe } from './requests/subscribe.js';
import { appConfig } from './config.js';

const PORT = parseInt(process.env['PORT'] || '5300', 10);

setOrigin(EaveOrigin.eave_github_app);

const app = express();
app.disable('x-powered-by');

/*
Using raw parsing rather than express.json() parser because of GitHub signature verification.
If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
*/
app.use(express.raw({ type: 'application/json' }));

const rootRouter = express.Router();
app.use('/github', rootRouter);
rootRouter.use(requestIntegrity);
rootRouter.use(loggingMiddleware);
rootRouter.use(standardEndpointsRouter);
// We don't attach any routes to the root path / because all requests to this app are prefixed with /github

// Github webhook
const webhookRouter = express.Router();
rootRouter.use('/events', webhookRouter);
webhookRouter.post('/', async (req, res) => {
  // POST /github/events
  await dispatch(req, res);
});

// Internal API
const internalApiRouter = express.Router();
rootRouter.use('/api', internalApiRouter);
internalApiRouter.use(originMiddleware);
internalApiRouter.use(signatureVerification(appConfig.eaveAppsBase));

internalApiRouter.post('/content', (req, res, next) => {
  // POST /github/api/content
  getSummary(req, res).catch(next);
});

internalApiRouter.post('/subscribe', (req, res, next) => {
  // POST /github/api/subscribe
  subscribe(req, res).catch(next);
});

// We use our own error handler. This error handler does not bubble up to Express's default error handling middleware.
app.use(exceptionHandlingMiddleware);

app.listen(PORT, '0.0.0.0', () => {
  eaveLogger.info(`App listening on port ${PORT}`);
});

export default app;
