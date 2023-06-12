import { applyShutdownHandlers } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import { app, addon } from './src/app.js';
import appConfig from './src/config.js';

const PORT = parseInt(process.env['PORT'] || '5400', 10);
const server = app.listen(PORT, '0.0.0.0', async () => {
  console.info(`App listening on port ${PORT}`, process.env['NODE_ENV']);
  if (appConfig.isDevelopment) {
    await addon.register();
  }
});

applyShutdownHandlers({ server });
