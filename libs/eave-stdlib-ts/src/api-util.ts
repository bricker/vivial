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
