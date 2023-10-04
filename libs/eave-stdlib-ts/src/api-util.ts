import Express, { IRouter, Request, Response, Router } from "express";
import { Server } from "http";
import { constants as httpConstants } from "node:http2";
import { cacheInitialized, getCacheClient } from "./cache.js";
import { sharedConfig } from "./config.js";
import { StatusResponseBody } from "./core-api/operations/status.js";
import { EaveApp } from "./eave-origins.js";
import { eaveLogger } from "./logging.js";
import { ExpressRoutingMethod } from "./types.js";
import { redact } from "./util.js";

/**
 * This function returns the status payload of the application.
 * 
 * @returns {StatusResponseBody} The status payload, which includes the service name, version, and status of the application.
 * 
 * @example
 * 
 * statusPayload();
 * // returns { service: 'appService', version: 'appVersion', status: 'OK' }
 * 
 */

export function statusPayload(): StatusResponseBody {
  return {
    service: sharedConfig.appService,
    version: sharedConfig.appVersion,
    status: "OK",
  };
}

```
/**
 * This function is responsible for creating a new router and defining a GET route at the root ("/") path.
 * The route handler is an asynchronous function that generates a status payload and checks if the cache has been initialized.
 * If the cache is initialized, it retrieves the cache client and sends a ping request to the cache server.
 * Finally, it sends a response with a status code of 200 and the generated payload in JSON format.
 * 
 * @returns {Router} The newly created router with the defined route.
 * 
 * @example
 * const router = StatusRouter();
 * app.use(router);
 */
```
export function StatusRouter(): Router {
  const router = Router();
  router.get("/", async (_req: Request, res: Response) => {
    const payload = statusPayload();

    if (cacheInitialized()) {
      const cacheClient = await getCacheClient();
      await cacheClient.ping();
    }

    res.status(200).json(payload);
  });

  return router;
}

/**
 * This function adds Google App Engine (GAE) lifecycle routes to the provided router.
 * 
 * @export
 * @param {Object} { router } - An object containing the router to which the routes will be added.
 * @param {IRouter} { router.router } - The router to which the routes will be added.
 * 
 * The function adds the following routes:
 * 
 * GET /_ah/start: This route is used by GAE to start an instance of the application. It responds with a 200 status code.
 * 
 * GET /_ah/stop: This route is used by GAE to stop an instance of the application. It responds with a 200 status code.
 * 
 * GET /_ah/warmup: This route is used by GAE to warm up an instance of the application. It initializes a cache client and connects to Redis, then responds with a 200 status code.
 */
export function addGAELifecycleRoutes({ router }: { router: IRouter }) {
  router.get("/_ah/start", (_req: Request, res: Response) => {
    res.sendStatus(200);
  });

  router.get("/_ah/stop", (_req: Request, res: Response) => {
    res.sendStatus(200);
  });

  router.get("/_ah/warmup", async (_req: Request, res: Response) => {
    // Initializes a client and connects to Redis
    const cacheClient = await getCacheClient();
    await cacheClient.ping();
    res.sendStatus(200);
  });
}

/**
 * This function handles the graceful shutdown of the server and the Redis cache client.
 * It first checks if the cache is initialized. If it is, it attempts to close the Redis connection.
 * Regardless of whether the cache is initialized or not, it then proceeds to close the HTTP server.
 * 
 * @export
 * @function gracefulShutdownHandler
 * @param {{ server: Server; }} { server } - An object containing the server to be shut down.
 * @returns {() => void} - A function that when called, initiates the shutdown process.
 * 
 * @example
 * // To use this function, pass in an object with the server to be shut down.
 * gracefulShutdownHandler({ server: myServer });
 */
export function gracefulShutdownHandler({
  server,
}: {
  server: Server;
}): () => void {
  return () => {
    if (cacheInitialized()) {
      getCacheClient()
        .then((client) => client.quit())
        .then(() => {
          eaveLogger.info("redis connection closed.");
        })
        .catch((e) => {
          eaveLogger.error(e);
        })
        .finally(() => {
          server.close(() => {
            eaveLogger.info("HTTP server closed");
          });
        });
    }
  };
}

```
/**
 * This function applies shutdown handlers to the server. It listens for SIGTERM and SIGINT signals 
 * and gracefully shuts down the server when either of these signals is received.
 * 
 * @export
 * @function applyShutdownHandlers
 * @param {{ server: Server }} { server } - An object containing the server to which the shutdown handlers will be applied.
 */
```
export function applyShutdownHandlers({ server }: { server: Server }) {
  const handler = gracefulShutdownHandler({ server });
  process.on("SIGTERM", handler);
  process.on("SIGINT", handler);
}

/**
 * This function retrieves headers from a given request, with the option to exclude or redact certain headers.
 * 
 * @param {Request} req - The request from which to retrieve headers.
 * @param {Set<string>} [excluded] - An optional set of headers to exclude from the returned object. These are case-insensitive.
 * @param {Set<string>} [redacted] - An optional set of headers to redact in the returned object. These are case-insensitive.
 * 
 * The function will always redact the 'authorization' and 'cookie' headers, regardless of the provided sets.
 * 
 * @returns {Object} An object containing the headers from the request. The keys are the header names in lowercase, and the values are the header values. If a header is in the redacted set, its value will be replaced with '[REDACTED]'.
 * 
 * @example
 * 
 * const req = {
 *   headers: {
 *     'Content-Type': 'application/json',
 *     'Authorization': 'Bearer token',
 *     'Cookie': 'session_id=123',
 *   },
 * };
 * const excluded = new Set(['content-type']);
 * const redacted = new Set(['authorization']);
 * 
 * const headers = getHeaders(req, excluded, redacted);
 * 
 * console.log(headers);
 * // Output: { 'cookie': '[REDACTED]' }
 */
export function getHeaders(
  req: Request,
  excluded?: Set<string>,
  redacted?: Set<string>,
): { [key: string]: string | undefined } {
  const redactedCaseInsensitive = new Set<string>(
    redacted ? Array.from(redacted).map((v) => v.toLowerCase()) : [],
  );

  const excludedCaseInsensitive = new Set<string>(
    excluded ? Array.from(excluded).map((v) => v.toLowerCase()) : [],
  );

  redactedCaseInsensitive.add(httpConstants.HTTP2_HEADER_AUTHORIZATION);
  redactedCaseInsensitive.add(httpConstants.HTTP2_HEADER_COOKIE);

  const logHeaders: { [key: string]: string | undefined } = {};

  Object.entries(req.headers).forEach(([k, v]) => {
    const lck = k.toLowerCase();
    if (!excludedCaseInsensitive.has(lck)) {
      const joined = v instanceof Array ? v.join(",") : v;
      logHeaders[lck] = redactedCaseInsensitive.has(lck)
        ? redact(joined)
        : joined;
    }
  });

  return logHeaders;
}

export abstract class ClientApiEndpointConfiguration {
  path: string;
  method: ExpressRoutingMethod;

  abstract audience: EaveApp;

  abstract get url(): string;

  ```
  /**
   * Constructs a new instance of the class.
   * 
   * @param {Object} options - The configuration object for the constructor.
   * @param {string} options.path - The path for the express route.
   * @param {ExpressRoutingMethod} [options.method=ExpressRoutingMethod.post] - The HTTP method for the express route. Defaults to 'POST'.
   */
  ```
  constructor({
    path,
    method = ExpressRoutingMethod.post,
  }: {
    path: string;
    method?: ExpressRoutingMethod;
  }) {
    this.path = path;
    this.method = method;
  }
}

export abstract class ServerApiEndpointConfiguration extends ClientApiEndpointConfiguration {
  teamIdRequired: boolean;
  authRequired: boolean;
  originRequired: boolean;
  signatureRequired: boolean;

  abstract get middlewares(): Express.Handler[];

  ```
  /**
   * Constructs a new instance of the class.
   * 
   * @param {Object} options - The configuration options for the instance.
   * @param {string} options.path - The path for the route.
   * @param {ExpressRoutingMethod} [options.method=ExpressRoutingMethod.post] - The HTTP method for the route. Defaults to 'post'.
   * @param {boolean} [options.teamIdRequired=true] - Indicates whether a team ID is required for the route. Defaults to true.
   * @param {boolean} [options.authRequired=true] - Indicates whether authentication is required for the route. Defaults to true.
   * @param {boolean} [options.originRequired=true] - Indicates whether the origin of the request is required for the route. Defaults to true.
   * @param {boolean} [options.signatureRequired=true] - Indicates whether a signature is required for the route. Defaults to true.
   */
  ```
  constructor({
    path,
    method = ExpressRoutingMethod.post,
    teamIdRequired = true,
    authRequired = true,
    originRequired = true,
    signatureRequired = true,
  }: {
    path: string;
    method?: ExpressRoutingMethod;
    teamIdRequired?: boolean;
    authRequired?: boolean;
    originRequired?: boolean;
    signatureRequired?: boolean;
  }) {
    super({ path, method });
    this.teamIdRequired = teamIdRequired;
    this.authRequired = authRequired;
    this.originRequired = originRequired;
    this.signatureRequired = signatureRequired;
  }
}

/**
 * Wraps an Express request handler function to ensure that the request is properly ended.
 * If the handler function forgets to end the request, this wrapper will do so to prevent hanging.
 * 
 * @param {Express.RequestHandler} func - The Express request handler function to be wrapped.
 * 
 * @returns {Express.RequestHandler} - The wrapped Express request handler function.
 * 
 * @example
 * const wrappedHandler = handlerWrapper(myHandler);
 * app.use('/my-route', wrappedHandler);
 * 
 * @throws Will forward any errors caught during the execution of the handler function to the next middleware.
 */
export function handlerWrapper(
  func: Express.RequestHandler,
): Express.RequestHandler {
  return async (
    req: Express.Request,
    res: Express.Response,
    next: Express.NextFunction,
  ) => {
    try {
      await func(req, res, next);
      res.end(); // Safety; if the handler forgets to end the request, it will hang.
    } catch (e: unknown) {
      next(e);
    }
  };
}

/**
 * This function is used to create a new route for the Express application.
 *
 * @export
 * @function makeRoute
 * @param {Object} params - An object containing the parameters for the function.
 * @param {Express.Router} params.router - The Express Router instance to which the route will be added.
 * @param {ServerApiEndpointConfiguration} params.config - The configuration object for the server API endpoint. It includes the HTTP method (e.g., 'GET', 'POST'), the path for the route, and any middleware functions to be used.
 * @param {Express.Handler} params.handler - The handler function to be executed when the route is accessed. This function takes in a request and a response object, and it sends a response back to the client.
 *
 * @example
 * makeRoute({
 *   router: express.Router(),
 *   config: {
 *     method: 'GET',
 *     path: '/api/data',
 *     middlewares: [authMiddleware, loggingMiddleware]
 *   },
 *   handler: (req, res) => {
 *     res.send('Hello World');
 *   }
 * });
 *
 * @returns {void} This function does not return anything. It simply adds a new route to the Express Router instance.
 */
export function makeRoute({
  router,
  config,
  handler,
}: {
  router: Express.Router;
  config: ServerApiEndpointConfiguration;
  handler: Express.Handler;
}) {
  router[config.method](
    config.path,
    ...config.middlewares,
    handlerWrapper(handler),
  );
}
