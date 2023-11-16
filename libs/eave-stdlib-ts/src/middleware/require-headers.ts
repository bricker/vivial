import { NextFunction, Request, Response } from "express";
import { LogContext, eaveLogger } from "../logging.js";

export function requireHeaders(
  ...headers: string[]
): (req: Request, res: Response, next: NextFunction) => void {
  return (req: Request, res: Response, next: NextFunction) => {
    const ctx = LogContext.load(res);
    for (const header of headers) {
      const value = req.header(header);
      if (!value) {
        eaveLogger.error(`Missing required header ${header}`, ctx);
        res.sendStatus(400);
        return;
      }
    }
    next();
  };
}
