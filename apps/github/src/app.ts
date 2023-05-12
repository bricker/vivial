import express from 'express';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util.js';
import dispatch from './dispatch.js';
import { getSummariesAndSubscribe } from './requests/content.js';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

app.use(express.raw({ type: 'application/json' }));
app.use(express.json());

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

app.use('/github', standardEndpointsRouter);

app.post('/github/events', async (req, res) => {
  await dispatch(req, res);
});

// internal routes

// TODO: maybe rename this route to be mroe descriptive? summarize + subscribe...?
app.post('/github/content', async (req, res) => {
  await getSummariesAndSubscribe(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
