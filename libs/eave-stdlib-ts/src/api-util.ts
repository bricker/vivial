import Express, { Handler } from "express";
import { constants as httpConstants } from 'node:http2';
import { IRouter, Request, Response, Router } from 'express';
import { Server } from 'http';
import { StatusResponseBody } from './core-api/operations/status.js';
import { sharedConfig } from './config.js';
import { getCacheClient, cacheInitialized } from './cache.js';
import {eaveLogger} from './logging.js';
import { redact } from './util.js';
import { ExpressRoutingMethod } from "./types.js";
import { EaveApp } from "./eave-origins.js";


export function statusPayload(): StatusResponseBody {
  return {
    service: sharedConfig.appService,
    version: sharedConfig.appVersion,
    status: 'OK',
  };
}

export function StatusRouter(): Router {
  const router = Router();
  router.get('/', async (_req: Request, res: Response) => {
    const payload = statusPayload();

    if (cacheInitialized()) {
      const cacheClient = await getCacheClient();
      await cacheClient.ping();
    }

    res.status(200).json(payload);
  });

  return router;
}

export function addGAELifecycleRoutes({ router }: { router: IRouter }) {
  router.get('/_ah/start', (_req: Request, res: Response) => {
    res.sendStatus(200);
  });

  router.get('/_ah/stop', (_req: Request, res: Response) => {
    res.sendStatus(200);
  });

  router.get('/_ah/warmup', async (_req: Request, res: Response) => {
    // Initializes a client and connects to Redis
    const cacheClient = await getCacheClient();
    await cacheClient.ping();
    res.sendStatus(200);
  });
}

export function gracefulShutdownHandler({ server }: { server: Server }): () => void {
  return () => {
    if (cacheInitialized()) {
      getCacheClient()
        .then((client) => client.quit())
        .then(() => { eaveLogger.info('redis connection closed.'); })
        .catch((e) => { eaveLogger.error(e); })
        .finally(() => {
          server.close(() => {
            eaveLogger.info('HTTP server closed');
          });
        });
    }
  };
}

export function applyShutdownHandlers({ server }: { server: Server }) {
  const handler = gracefulShutdownHandler({ server });
  process.on('SIGTERM', handler);
  process.on('SIGINT', handler);
}

export function getHeaders(req: Request, excluded?: Set<string>, redacted?: Set<string>): { [key: string]: string | undefined } {
  const redactedCaseInsensitive = new Set<string>(
    redacted
      ? Array.from(redacted).map((v) => v.toLowerCase())
      : [],
  );

  const excludedCaseInsensitive = new Set<string>(
    excluded
      ? Array.from(excluded).map((v) => v.toLowerCase())
      : [],
  );

  redactedCaseInsensitive.add(httpConstants.HTTP2_HEADER_AUTHORIZATION);
  redactedCaseInsensitive.add(httpConstants.HTTP2_HEADER_COOKIE);

  const logHeaders: { [key: string]: string | undefined } = {};

  Object.entries(req.headers).forEach(([k, v]) => {
    const lck = k.toLowerCase();
    if (!excludedCaseInsensitive.has(lck)) {
      const joined = v instanceof Array ? v.join(',') : v;
      logHeaders[lck] = redactedCaseInsensitive.has(lck) ? redact(joined) : joined;
    }
  });

  return logHeaders;
}

export abstract class ClientApiEndpointConfiguration {
  path: string;
  method: ExpressRoutingMethod;

  abstract audience: EaveApp;

  abstract get url(): string;

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

export function handlerWrapper(func: Express.RequestHandler): Express.RequestHandler {
  return async (req: Express.Request, res: Express.Response, next: Express.NextFunction) => {
    try {
      await func(req, res, next);
      res.end(); // Safety; if the handler forgets to end the request, it will hang.
    } catch (e: unknown) {
      next(e);
    }
  };
}

export function makeRoute({ router, config, handler }: { router: Express.Router, config: ServerApiEndpointConfiguration, handler: Express.Handler }) {
  router[config.method](config.path, ...config.middlewares, handlerWrapper(handler));
}
