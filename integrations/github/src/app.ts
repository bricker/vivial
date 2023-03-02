import express, { Response } from 'express';
import dispatch from './dispatch';

const PORT = parseInt(process.env['PORT'] || '8080', 10);
const app = express();

app.use(express.raw({ type: 'application/json' }));

app.use((req, _, next) => {
  console.info('Request: ', req.url);
  next();
});

const statusHandler = (_: unknown, res: Response) => {
  res.json({ status: '1', service: 'github' })
    .status(200)
    .end();
};

app.get('/status', statusHandler);
app.get('/_ah/start', statusHandler);
app.get('/_ah/stop', statusHandler);
app.get('/_ah/warmup', statusHandler);

app.post('/webhook/github', async (req, res) => {
  await dispatch(req, res);
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`App listening on port ${PORT}`);
});

export default app;
