import express from 'express';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import dispatch from './dispatch.js';
import { getSummary } from './requests/content.js';
import { subscribe } from './requests/subscribe.js';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

/*
Using raw parsing rather than express.json() parser because of GitHub signature verification.
If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
*/
app.use(express.raw({ type: 'application/json' }));

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

app.use('/github', standardEndpointsRouter);

app.post('/github/events', async (req, res) => {
  await dispatch(req, res);
});

// internal routes

// TODO: signing or something??
app.post('/github/content', async (req, res) => {
  await getSummary(req, res);
});

app.post('/github/subscribe', async (req, res) => {
  await subscribe(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
