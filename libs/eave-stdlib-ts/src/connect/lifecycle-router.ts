import { Request, Response, Router } from "express";
import AddOnFactory, { AddOn } from 'atlassian-connect-express';
import { registerConnectInstallation } from "../core-api/operations/connect.js";
import { AtlassianProduct } from "../core-api/models/connect.js";
import { EaveOrigin } from "../eave-origins.js";
import eaveLogger from '../logging.js';

export function LifecycleRouter({ addon, product, eaveOrigin }: { addon: AddOn, product: AtlassianProduct, eaveOrigin: EaveOrigin }): Router {
  const router = Router();

  // A custom implementation of the atlassian-connect-express built-in install handler.
  router.post('/installed', addon.verifyInstallation(), async (req: Request, res: Response) => {
    const settings: AddOnFactory.ClientInfo = req.body;

    await registerConnectInstallation({
      origin: eaveOrigin,
      input: {
        connect_integration: {
          product,
          client_key: settings.clientKey,
          base_url: settings.baseUrl,
          shared_secret: settings.sharedSecret,
          description: settings.description,
        },
      },
    });

    res.status(204).send();
  });

  router.post('/enabled', async (req: Request /* res: Response */) => {
    eaveLogger.info({ message: 'received enabled lifecycle event', body: req.body, product, eaveOrigin });
  });

  router.post('/disabled', async (req: Request /* res: Response */) => {
    eaveLogger.info({ message: 'received disabled lifecycle event', body: req.body, product, eaveOrigin });
  });

  router.post('/uninstalled', addon.verifyInstallation(), async (req: Request /* res: Response */) => {
    eaveLogger.info({ message: 'received uninstalled lifecycle event', body: req.body, product, eaveOrigin });
  });

  return router;
}
