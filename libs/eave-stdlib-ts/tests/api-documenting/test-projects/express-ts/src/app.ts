import express, { json } from 'express';
import { V1Router } from './endpoints/v1/routes.js';

const app = express();
app.use(json());

const rootRouter = express.Router();
app.use('/api', rootRouter);
rootRouter.use('/v1', V1Router());
