import express from 'express';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import dispatch from './dispatch.js';
import { appConfig } from './config.js';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

app.use(express.raw({ type: 'application/json' }));

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

const rootRouter = express.Router();
rootRouter.use(standardEndpointsRouter);

rootRouter.post('/events', async (req, res) => {
  await dispatch(req, res);
});

app.use(appConfig.routePrefix, rootRouter);

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
