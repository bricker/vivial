import express from 'express';
import { StatusResponseBody } from './core-api/operations/status.js';
import { sharedConfig } from './config.js';

export function statusPayload(): StatusResponseBody {
  return {
    service: sharedConfig.appService,
    version: sharedConfig.appVersion,
    status: 'OK',
  };
}

export const standardEndpointsRouter = express.Router();

standardEndpointsRouter.get('/status', (_: express.Request, res: express.Response) => {
  const payload = statusPayload();
  res.json(payload).status(200).end();
});


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
