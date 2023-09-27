import { NextFunction, Request, Response } from "express";
import { EAVE_CTX_KEY } from "../headers.js";
import { LogContext } from "../logging.js";

export function requestIntegrityMiddleware(
  _req: Request,
  res: Response,
  next: NextFunction,
): void {
  const ctx = LogContext.load(res);
  res.locals[EAVE_CTX_KEY] = ctx;
  next();
}
