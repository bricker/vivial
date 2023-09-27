import { NextFunction, Request, Response } from "express";
import onFinished from "on-finished";
import { LogContext, eaveLogger } from "../logging.js";

export function requestLoggingMiddleware(
  req: Request,
  res: Response,
  next: NextFunction,
) {
  const ctx = LogContext.load(res);
  eaveLogger.info(
    `Server Request Start: ${ctx.eave_request_id}: ${req.method} ${req.originalUrl}`,
    ctx,
  );

  onFinished(res, (err, res2) => {
    const ctx2 = LogContext.load(res2);
    if (err) {
      eaveLogger.error(err, ctx2);
    }
    eaveLogger.info(
      `Server Request End: ${ctx2.eave_request_id}: ${req.method} ${req.originalUrl}`,
      ctx,
    );
  });

  next();
}
