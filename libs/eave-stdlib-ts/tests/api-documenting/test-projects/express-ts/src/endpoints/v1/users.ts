import { Request, Response } from "express";

const users: string[] = ["Liam", "Lana", "Leilenah", "Bryan"];

export function getUsers(req: Request, res: Response) {
  res.status(200).json(users);
}

export function getUser(req: Request, res: Response) {
  const userIdParam = req.params["user_id"]!;
  const userIndex = parseInt(userIdParam, 10);
  const user = users[userIndex];
  if (!user) {
    res.sendStatus(404);
  } else {
    res.status(200).json(user);
  }
}

export function createUser(req: Request, res: Response) {
  const user = req.body["user"];
  users.push(user);
  res.sendStatus(201);
}

export function updateUser(req: Request, res: Response) {
  const userIdParam = req.params["user_id"]!;
  const userIndex = parseInt(userIdParam, 10);
  const user = users[userIndex];
  if (!user) {
    res.sendStatus(404);
  } else {
    const newUser = req.body["user"];
    users[userIndex] = newUser;
    res.status(200);
  }
}

export function deleteUser(req: Request, res: Response) {
  const userIdParam = req.params["user_id"]!;
  const userIndex = parseInt(userIdParam, 10);
  const user = users[userIndex];
  if (!user) {
    res.sendStatus(404);
  } else {
    delete users[userIndex];
    res.status(200);
  }
}
