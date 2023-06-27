import express from 'express';
import ace from 'atlassian-connect-express';
import { applyAtlassianSecurityPolicyMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/connect/security-policy-middlewares.js';
import { GAELifecycleRouter, StatusRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import EaveApiAdapter from '@eave-fyi/eave-stdlib-ts/src/connect/eave-api-store-adapter.js';
import { helmetMiddleware, applyCommonRequestMiddlewares, applyCommonResponseMiddlewares, applyInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { InternalApiRouter } from './api/routes.js';
import { WebhookRouter, applyWebhookMiddlewares } from './events/routes.js';
import eaveConfig from './config.js';

// This <any> case is necessary to tell Typescript to effectively ignore this expression.
// ace.store is exported in the javascript implementation, but not in the typescript type definitions,
// so Typescript (rightfully) shows an error.
(<any>ace).store.register('eave-api-store', EaveApiAdapter);

export const app = express();
export const addon = ace(app, {
  config: {
    descriptorTransformer: (descriptor, config): any => {
      descriptor.key = eaveConfig.eaveJiraAppKey;
      descriptor.name = eaveConfig.eaveJiraAppName;

      if (config.environment() === 'production') {
        descriptor.baseUrl = `${eaveConfig.eaveAppsBase}/jira`;
      }
      return descriptor;
    },
  },
});

app.use(helmetMiddleware());
applyAtlassianSecurityPolicyMiddlewares({ app });
applyCommonRequestMiddlewares({ app });
applyInternalApiMiddlewares({ path: '/jira/api', app });
applyWebhookMiddlewares({ app, addon, path: '/jira/events' });

app.use(GAELifecycleRouter());

const rootRouter = express.Router();
app.use('/jira', rootRouter);

rootRouter.use(StatusRouter());
rootRouter.use('/events', WebhookRouter({ addon }));
rootRouter.use('/api', InternalApiRouter({ addon }));

applyCommonResponseMiddlewares({ app });
