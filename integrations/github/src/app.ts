import express, { Response } from 'express';
import dispatch from './dispatch';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

app.use(express.raw({ type: 'application/json' }));

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

app.get('/github/status', (_: unknown, res: Response) => {
  res.json({ service: 'github', status: 'OK' })
    .status(200)
    .end();
});

app.post('/github/events', async (req, res) => {
  await dispatch(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
