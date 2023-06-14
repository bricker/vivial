import { Request, Response, Router } from 'express';
import { Server } from 'http';
import { StatusResponseBody } from './core-api/operations/status.js';
import { sharedConfig } from './config.js';
import getCacheClient, { cacheInitialized } from './cache.js';
import eaveLogger from './logging.js';

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

  router.get('/_ah/warmup', async (_req: Request, res: Response) => {
    const cacheClient = await getCacheClient(); // Initializes a client and connects to Redis
    await cacheClient.ping();
    res.sendStatus(200);
  });

  return router;
}

export function gracefulShutdownHandler({ server }: { server: Server }): () => void {
  return () => {
    if (cacheInitialized()) {
      getCacheClient()
        .then((client) => client.quit())
        .then(() => { eaveLogger.info({ message: 'redis connection closed.' }); })
        .catch((e) => { eaveLogger.error({ message: e.stack }); })
        .finally(() => {
          server.close(() => {
            eaveLogger.info({ message: 'HTTP server closed' });
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

// def get_headers(
//   scope: HTTPScope, excluded: Optional[list[str]] = None, redacted: Optional[list[str]] = None
// ) -> dict[str, str]:
//   """
//   This function doesn't support multiple headers with the same name.
//   It will always choose the "first" one (from whatever order the ASGI server sent).
//   See here for details about the scope["headers"] object:
//   https://asgi.readthedocs.io/en/latest/specs/www.html#http-connection-scope
//   """
//   if excluded is None:
//       excluded = []
//   if redacted is None:
//       redacted = []

//   return {
//       n.decode(): (v.decode() if n.decode().lower() not in redacted else redact(v.decode()))
//       for [n, v] in scope["headers"]
//       if n.decode().lower() not in excluded
//   }
