import assert from 'node:assert';
import { constants as httpConstants } from 'node:http2';
import Express from 'express';
import eaveLogger, { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { EaveApp } from '@eave-fyi/eave-stdlib-ts/src/eave-origins.js';
import getCacheClient, { Cache } from '@eave-fyi/eave-stdlib-ts/src/cache.js';
import { commonInternalApiMiddlewares, rawJsonBody } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import { githubAppClient } from '../lib/octokit-util.js';
import {runApiDocumentation} from '../tasks/api-documentation.js';

export function OfflineTaskRouter(): Express.Router {
  const router = Express.Router();
  router.use(commonInternalApiMiddlewares);
  router.use(jsonParser);

  router.post('/run-api-documentation', async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
      const ctx = LogContext.load(res);
      await runApiDocumentation({ req, res, ctx });
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
