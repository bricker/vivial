import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

It seems like you've provided an incomplete input. Could you please provide more details or context? I'm here to help with TypeScript doc comments.
export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
  /*
  Using raw parsing rather than express.json() parser because of GitHub signature verification.
  If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
  */
  app.use(path, raw({ type: 'application/json', limit: '5mb' }));
}

It seems like you're trying to start a TypeScript doc comment. Here's an example of how you can do it:

```typescript
/**
 * This is a TypeScript doc comment.
 */
```

In TypeScript, doc comments are used to provide detailed explanations about the code, which can include descriptions of functions, classes, interfaces, etc. They are written inside `/** */` tags.
export function WebhookRouter(): Router {
  const router = Router();

  router.post('/', async (req: Request, res: Response, next: NextFunction) => {
    try {
      await dispatch(req, res);
      res.end(); // safety
    } catch (e: unknown) {
      next(e);
    }
  });

  return router;
}
