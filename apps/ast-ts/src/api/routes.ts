import { NextFunction, Request, Response, Router } from 'express';
import { GenericRequestBody } from '@eave-fyi/eave-stdlib-ts/src/requests';
import * as acorn from 'acorn';

export function InternalApiRouter(): Router {
  const router = Router();

  router.post('/parse', async (req: Request, res: Response, next: NextFunction) => {
    try {
      const reqBody = <GenericRequestBody>req.body;
      const ast = acorn.parse(reqBody.data, {ecmaVersion: "latest"})
      res.send(ast)
    } catch (e: unknown) {
        next(e);
    }
  });

  return router;
}
