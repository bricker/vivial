import express from 'express';
import ace from 'atlassian-connect-express';
import helmet from 'helmet';
import { exceptionHandlingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/exception-handling.js';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification.js';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity.js';
import { requestLoggingMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/logging.js';
import { originMiddleware } from '@eave-fyi/eave-stdlib-ts/src/middleware/origin.js';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import OpenAIClient, { OpenAIModel } from '@eave-fyi/eave-stdlib-ts/src/openai.js';
import { searchDocuments } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/documents.js';
import { queryConnectInstallation } from '@eave-fyi/eave-stdlib-ts/src/core-api/operations/connect.js';
import { AtlassianProduct } from '@eave-fyi/eave-stdlib-ts/src/core-api/models/connect.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import { IncomingMessage } from 'node:http';
import { LifecycleRouter } from '@eave-fyi/eave-stdlib-ts/src/connect/lifecycle-router.js';
import getCacheClient from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import { CommentCreatedEventPayload, ContentType, User } from './types.js';
import appConfig from './config.js';

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
app.use(helmet.xPoweredBy());

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
rootRouter.use(requestLoggingMiddleware);
rootRouter.use(standardEndpointsRouter);

// // Redirect root path to /atlassian-connect.json,
// // which will be served by atlassian-connect-express.
// rootRouter.get('/', (req, res) => {
//   res.redirect('/jira/atlassian-connect.json');
// });

// webhooks
const webhookRouter = express.Router();
rootRouter.use('/events', webhookRouter);

const lifecycleRouter = LifecycleRouter({ addon, product: AtlassianProduct.jira, eaveOrigin: appConfig.eaveOrigin });
webhookRouter.use(lifecycleRouter);

webhookRouter.post('/', addon.authenticate(), async (req /* , res */) => {
  // FIXME: Dispatch different events
  // FIXME: Redact auth header
  eaveLogger.debug({ message: 'received webhook event', body: req.body, headers: req.headers });
  const openaiClient = await OpenAIClient.getAuthedClient();
  const payload = <CommentCreatedEventPayload>req.body;
  const client = addon.httpClient(req);

  if (payload.comment.author.accountType === 'app') {
    eaveLogger.info('Ignoring app comment');
    return;
  }

  // [~accountid:712020:d50089b8-586c-4f54-a3ad-db70381e4cae]
  const mentionAccountIds = payload.comment.body.match(/\[~accountid:(.+?)\]/i);
  if (!mentionAccountIds) {
    eaveLogger.info('No mentions in this message, ignoring');
    return;
  }

  // We have to use an old-fashioned Promise chain this way because the atlassian express library
  // uses the request library directly and uses the callback function interface.
  const eaveMentioned = await Promise.any(mentionAccountIds.map((accountId) => {
    return new Promise<boolean>((resolve, reject) => {
      client.get({
        url: '/rest/api/3/user',
        qs: { accountId },
      }, (err: any, response: IncomingMessage, body: string) => {
        if (err) {
          reject();
          return;
        }
        if (response.statusCode === 200) {
          const user = <User>JSON.parse(body);
          if (user.accountType === 'app' && user.displayName === 'Eave for Jira') {
            resolve(true);
          } else {
            reject();
          }
        }
      }).catch(reject);
    });
  }));

  if (!eaveMentioned) {
    eaveLogger.info('Eave not mentioned, ignoring');
    return;
  }

  const prompt = [
    'Is the following message asking you to look up some existing documentation? Say either Yes or No.',
    'Message:',
    '###',
    payload.comment.body,
    '###',
  ].join('\n');

  const openaiResponse = await openaiClient.createChatCompletion({
    messages: [
      { role: 'user', content: prompt },
    ],
    model: OpenAIModel.GPT4,
  });

  eaveLogger.debug('OpenAI response', { openaiResponse });

  if (!openaiResponse.match(/yes/i)) {
    eaveLogger.debug('Comment ignored');
    return;
  }

  const connectInstallation = await queryConnectInstallation({
    origin: appConfig.eaveOrigin,
    input: {
      connect_integration: {
        product: AtlassianProduct.jira,
        client_key: client.clientKey,
      },
    },
  });

  const teamId = connectInstallation.team?.id;
  if (!teamId) {
    eaveLogger.warn({ message: 'No teamId available', clientKey: client.clientKey });
    return;
  }

  const searchResults = await searchDocuments({
    origin: appConfig.eaveOrigin,
    teamId,
    input: {
      query: payload.comment.body,
    },
  });

  if (payload.issue !== undefined) {
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
              content: searchResults.documents.map((document) => (
                {
                  type: ContentType.text,
                  text: document.title,
                  marks: [
                    {
                      type: ContentType.link,
                      attrs: {
                        href: document.url,
                        title: document.title,
                      },
                    },
                  ],
                }
              )),
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
internalApiRouter.post('/_', (/* req, res, next */) => {
  // not used, just here for placeholder
});

app.use(exceptionHandlingMiddleware);

const PORT = parseInt(process.env['PORT'] || '5500', 10);
const server = app.listen(PORT, '0.0.0.0', async () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    await addon.register();
  }
});

// TODO: move this into stdlib
const gracefulShutdownHandler = () => {
  getCacheClient
    .then((client) => client.quit())
    .then(() => { eaveLogger.info('redis connection closed.'); })
    .catch((e) => { eaveLogger.error(e); });

  server.close(() => {
    eaveLogger.info('HTTP server closed');
  });
};

process.on('SIGTERM', gracefulShutdownHandler);
process.on('SIGINT', gracefulShutdownHandler);
