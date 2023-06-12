import { Request, Response, NextFunction } from 'express';

export function requireHeaders(...headers: string[]): ((req: Request, res: Response, next: NextFunction) => void) {
  return (req: Request, res: Response, next: NextFunction) => {
    for (const header of headers) {
      const value = req.header(header);
      if (!value) {
        res.sendStatus(400).end();
        return;
      }
    }
    next();
  };
}
