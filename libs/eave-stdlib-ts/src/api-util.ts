import express from 'express';
import { Status } from './core-api/operations';
import { sharedConfig } from './config';

export function statusPayload(): Status.ResponseBody {
  return {
    "service": sharedConfig.appService,
    "version": sharedConfig.appVersion,
    "status": "OK",
  }
}

export const standardEndpointsRouter = express.Router();

standardEndpointsRouter.get('/status', (_: express.Request, res: express.Response) => {
  const payload = statusPayload();
  res.json(payload).status(200).end();
});
