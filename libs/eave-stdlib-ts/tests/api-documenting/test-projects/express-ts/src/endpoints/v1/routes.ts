import { Request, Response, Router } from 'express';
import { getLists, getList, createList, updateList, deleteList } from './lists.js';
import { getUsers, getUser, createUser, updateUser, deleteUser } from './users.js';

export function V1Router(): Router {
  const router = Router();

  router.get('/lists', async (req: Request, res: Response) => {
    await getLists(req, res);
  });

  router.get('/lists/:list_id', async (req: Request, res: Response) => {
    await getList(req, res);
  });

  router.post('/lists', async (req: Request, res: Response) => {
    await createList(req, res);
  });

  router.patch('/lists/:list_id', async (req: Request, res: Response) => {
    await updateList(req, res);
  });

  router.delete('/lists/:list_id', async (req: Request, res: Response) => {
    await deleteList(req, res);
  });

  router.get('/users', async (req: Request, res: Response) => {
    await getUsers(req, res);
  });

  router.get('/users/:user_id', async (req: Request, res: Response) => {
    await getUser(req, res);
  });

  router.post('/users', async (req: Request, res: Response) => {
    await createUser(req, res);
  });

  router.patch('/users/:user_id', async (req: Request, res: Response) => {
    await updateUser(req, res);
  });

  router.delete('/users/:user_id', async (req: Request, res: Response) => {
    await deleteUser(req, res);
  });

  return router;
}
