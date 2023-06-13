import { Router } from 'express';
import { AddOn } from 'atlassian-connect-express';

export function InternalApiRouter({ addon }: {addon: AddOn}): Router {
  const router = Router();
  // Not currently used
  return router;
}
