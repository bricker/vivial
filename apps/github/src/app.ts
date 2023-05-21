import express from 'express';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging';
import { standardEndpointsRouter } from '@eave-fyi/eave-stdlib-ts/src/api-util';
import { signatureVerification } from '@eave-fyi/eave-stdlib-ts/src/middleware/signature-verification';
import { requestIntegrity } from '@eave-fyi/eave-stdlib-ts/src/middleware/request-integrity';
import { setOrigin } from '@eave-fyi/eave-stdlib-ts/src/lib/requests';
import { EaveOrigin } from '@eave-fyi/eave-stdlib-ts/src/eave-origins';
import dispatch from './dispatch';
import { getSummary } from './requests/content';
import { subscribe } from './requests/subscribe';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

setOrigin(EaveOrigin.eave_github_app);

/*
Using raw parsing rather than express.json() parser because of GitHub signature verification.
If even 1 byte were different after passing through JSON.parse and then the signature verification would fail.
*/
app.use(express.raw({ type: 'application/json' }));

// middleware
app.use('/github/api', requestIntegrity);
app.use('/github/api', signatureVerification);
app.use((req, _, next) => {
  eaveLogger.info('Request: ', req.url);
  next();
});

app.use('/github', standardEndpointsRouter);

app.post('/github/events', async (req, res) => {
  await dispatch(req, res);
});

// internal routes

app.post('/github/api/content', async (req, res) => {
  await getSummary(req, res);
});

app.post('/github/api/subscribe', async (req, res) => {
  await subscribe(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  eaveLogger.info(`App listening on port ${PORT}`);
});

export default app;
