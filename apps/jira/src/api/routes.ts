import { Router } from 'express';
import { AddOn } from 'atlassian-connect-express';
import { commonInternalApiMiddlewares } from '@eave-fyi/eave-stdlib-ts/src/middleware/common-middlewares.js';
import { jsonParser } from '@eave-fyi/eave-stdlib-ts/src/middleware/body-parser.js';

export function InternalApiRouter(_args: {addon: AddOn}): Router {
  const router = Router();
  router.use(...commonInternalApiMiddlewares);
  router.use(jsonParser);

  // Not currently used
  return router;
}
