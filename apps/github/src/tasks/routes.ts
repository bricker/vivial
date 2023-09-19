import Express from 'express';
import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { RunApiDocumentationTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/run-api-documentation-task.js';
import { runApiDocumentation } from './api-documentation.js';
import { GithubEventHandlerTaskOperation } from '@eave-fyi/eave-stdlib-ts/src/github-api/operations/event-handler-task.js';

export function OfflineTaskRouter(): Express.Router {
  const router = Express.Router();

  router.post(RunApiDocumentationTaskOperation.config.path, ...RunApiDocumentationTaskOperation.config.middlewares, async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
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