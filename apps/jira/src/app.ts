import express from 'express';
import ace from 'atlassian-connect-express';
import helmet from 'helmet';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { loggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import appConfig from './config.js';
import EaveApiAdapter from './eave-api-adapter.js';
import { CommentCreatedEventPayload, ContentType } from './types.js';

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register('eave-api-store', EaveApiAdapter);

const app = express();
const addon = ace(app);

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
app.use('/jira', rootRouter);
rootRouter.use(requestIntegrity);
rootRouter.use(loggingMiddleware);
rootRouter.use(standardEndpointsRouter);

// // Redirect root path to /atlassian-connect.json,
// // which will be served by atlassian-connect-express.
// rootRouter.get('/', (req, res) => {
//   res.redirect('/jira/atlassian-connect.json');
// });

// webhooks
const webhookRouter = express.Router();
rootRouter.use('/events', webhookRouter);

webhookRouter.post('/', addon.authenticate(), async (req, res) => {
  eaveLogger.info('received webhook event', req.body);
  eaveLogger.info('received webhook event', req.headers);

  const payload = <CommentCreatedEventPayload>req.body;
  const client = addon.httpClient(req);

  if (payload.comment.author.accountType === 'app') {
    eaveLogger.info('Ignoring app comment');
    return;
  }

  if (payload.issue) {
    await client.post({
      url: `/rest/api/3/issue/${payload.issue.id}/comment`,
      json: true,
      body: {
        body: {
          type: ContentType.doc,
          version: 1,
          content: [
            {
              type: 'paragraph',
              content: [
                {
                  type: ContentType.text,
                  text: 'Eave',
                  marks: [
                    {
                      type: ContentType.link,
                      attrs: {
                        href: 'https://www.eave.fyi',
                        title: 'Eave Website',
                      },
                    },
                  ],
                },
              ],
            },
          ],
        },
      },
    });
  }
});

// API
const internalApiRouter = express.Router();
rootRouter.use('/api', internalApiRouter);
internalApiRouter.use(originMiddleware);
internalApiRouter.use(signatureVerification(appConfig.eaveAppsBase));
internalApiRouter.post('/_', (req, res, next) => {
  // not used, just here for placeholder
});

app.use(exceptionHandlingMiddleware);

const PORT = parseInt(process.env['PORT'] || '5500', 10);
app.listen(PORT, '0.0.0.0', () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    addon.register();
  }
});
