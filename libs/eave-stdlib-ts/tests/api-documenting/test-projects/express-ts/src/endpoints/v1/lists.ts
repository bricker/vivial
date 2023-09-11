import { Request, Response } from 'express';

let lists: string[] = ['TODO', 'Personal', 'Work', 'Shopping'];

export function getLists(req: Request, res: Response) {
  res.status(200).json(lists);
}

export function getList(req: Request, res: Response) {
  const listIdParam = req.params['list_id']!;
  const listIndex = parseInt(listIdParam, 10);
  const list = lists[listIndex];
  if (!list) {
    res.sendStatus(404);
  } else {
    res.status(200).json(list);
  }
}

export function createList(req: Request, res: Response) {
  const list = req.body['list'];
  lists.push(list);
  res.sendStatus(201);
}

export function updateList(req: Request, res: Response) {
  const listIdParam = req.params['list_id']!;
  const listIndex = parseInt(listIdParam, 10);
  const list = lists[listIndex];
  if (!list) {
    res.sendStatus(404);
  } else {
    const newList = req.body['list'];
    lists[listIndex] = newList;
    res.status(200);
  }
}

export function deleteList(req: Request, res: Response) {
  const listIdParam = req.params['list_id']!;
  const listIndex = parseInt(listIdParam, 10);
  const list = lists[listIndex];
  if (!list) {
    res.sendStatus(404);
  } else {
    delete lists[listIndex];
    res.status(200);
  }
}
