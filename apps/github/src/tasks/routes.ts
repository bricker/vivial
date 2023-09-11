import Express from 'express';
import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { commonInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';
import { runApiDocumentation } from '../tasks/api-documentation.js';

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
