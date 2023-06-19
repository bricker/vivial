import { Request, Response, NextFunction } from 'express';
import eaveLogger from '../logging.js';
import { getEaveState } from '../lib/request-state.js';

export function requireHeaders(...headers: string[]): ((req: Request, res: Response, next: NextFunction) => void) {
  return (req: Request, res: Response, next: NextFunction) => {
    const eaveState = getEaveState(res);
    for (const header of headers) {
      const value = req.header(header);
      if (!value) {
        eaveLogger.error({ message: `Missing required header ${header}`, eaveState });
        res.sendStatus(400);
        return;
      }
    }
    next();
  };
}
