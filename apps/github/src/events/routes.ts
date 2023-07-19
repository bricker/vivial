Updated Document
###

```
import { NextFunction, Request, Response, Router, raw, Express } from 'express';
import dispatch from '../dispatch.js';

export function applyWebhookMiddlewares({ app, path }:{ app: Express, path: string }) {
/*
The function "applyWebhookMiddlewares" accepts an object with the properties 'app' and 'path'. These represent the Express application and the path for applying webhook middlewares respectively. 

The middleware used here is the 'raw' middleware from Express with a configuration to parse incoming requests with a JSON payload.

Please note that we are using raw parsing instead of the express.json() parser due to GitHub signature verification concerns. In the scenario where even 1 byte is different after passing through JSON.parse, the signature verification would fail. 

The limit has been set to '5mb' to manage the payload size.
*/
app.use(path, raw({ type: 'application/json', limit: '5mb' }));
}

export function WebhookRouter(): Router {
const router = Router();

/*
The function "WebhookRouter" involves setting up a POST route at the root ('/') of the router.

In the anonymous function for handling this route, the request and response objects are passed to the dispatch function imported from '../dispatch.js', and is awaited to ensure the completion of any asynchronous actions. 

If everything proceeds without an error, the response object is ended using 'res.end()' for safety to ensure no more data is written to the response stream.

In case an error is thrown during the asynchronous operation, the error is caught and forwarded to the next middleware in the express middleware chain for error handling by calling 'next(e)'.
*/
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

```
###