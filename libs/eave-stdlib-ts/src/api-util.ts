import { Request, Response, Router } from 'express';
import { Server } from 'http';
import { StatusResponseBody } from './core-api/operations/status.js';
import { sharedConfig } from './config.js';
import getCacheClient, { cacheInitialized } from './cache.js';
import eaveLogger from './logging.js';
import headers from './headers.js';
import { redact } from './util.js';
import { loadExtensionMap } from './language-mapping.js';

export function statusPayload(): StatusResponseBody {
  return {
    service: sharedConfig.appService,
    version: sharedConfig.appVersion,
    status: 'OK',
  };
}

export function StatusRouter(): Router {
  const router = Router();
  router.get('/status', async (_req: Request, res: Response) => {
    const payload = statusPayload();

    if (cacheInitialized()) {
      const cacheClient = await getCacheClient();
      await cacheClient.ping();
    }

    res.status(200).json(payload);
  });

  return router;
}

export function GAELifecycleRouter(): Router {
  const router = Router();

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

    await loadExtensionMap();
    res.sendStatus(200);
  });

  return router;
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
  const redactedcp = new Set<string>(redacted);
  redactedcp.add(headers.AUTHORIZATION_HEADER);
  redactedcp.add(headers.COOKIE_HEADER);

  const logHeaders: { [key: string]: string | undefined } = {};

  Object.entries(req.headers).forEach(([k, v]) => {
    if (!excluded?.has(k)) {
      const joined = v instanceof Array ? v.join(',') : v;
      logHeaders[k] = redactedcp.has(k) ? redact(joined) : joined;
    }
  });

  return logHeaders;
}

export function constructUrl(req: Request): string {
  const audience = req.header(headers.HOST);
  const path = req.originalUrl;

  return `https://${audience}${path}`;
}
