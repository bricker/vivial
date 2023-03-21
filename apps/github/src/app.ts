import express from 'express';
import { addStandardEndpoints } from '@eave-fyi/eave-stdlib-ts/src/api-util';
import dispatch from './dispatch.js';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

app.use(express.raw({ type: 'application/json' }));

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

addStandardEndpoints(app, '/github');

app.post('/github/events', async (req, res) => {
  await dispatch(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
