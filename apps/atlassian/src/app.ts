import express from 'express';
import ace from 'atlassian-connect-express';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { appConfig, connectAppDescriptor } from './config.js';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();
const addon = ace(app);

app.use(express.json());

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

app.use(addon.middleware());

const rootRouter = express.Router();
rootRouter.use(standardEndpointsRouter);
rootRouter.get('/connect-manifest.json', (_: express.Request, res: express.Response) => {
  res.json(connectAppDescriptor).status(200).end();
});

rootRouter.post('/events/installed', /* authHeaderAsymmetricJwtMiddleware, */ async (_, res) => {
  // const { baseUrl: url, clientKey, sharedSecret } = req.body;

  // const data = {
  //   url,
  //   sharedSecret,
  //   clientKey,
  // };

  res.sendStatus(204);
});

rootRouter.post('/events/enabled', /* authHeaderSymmetricJwtMiddleware, */ async (_, res) => {
  res.sendStatus(204);
});

rootRouter.post('/events/disabled', /* authHeaderSymmetricJwtMiddleware, */ async (_, res) => {
  res.sendStatus(204);
});

rootRouter.post('/events/uninstalled', /* authHeaderAsymmetricJwtMiddleware, */ async (_, res) => {
  // const { clientKey } = req.body;
  res.sendStatus(204);
});

app.use(appConfig.routePrefix, rootRouter);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
