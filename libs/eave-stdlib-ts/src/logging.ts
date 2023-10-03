import { LoggingWinston } from "@google-cloud/logging-winston";
import { Request, Response } from "express";
import { v4 as uuidv4 } from "uuid";
import winston from "winston";
import { getHeaders } from "./api-util.js";
import { sharedConfig } from "./config.js";
import {
  EAVE_ACCOUNT_ID_HEADER,
  EAVE_CTX_KEY,
  EAVE_ORIGIN_HEADER,
  EAVE_REQUEST_ID_HEADER,
  EAVE_TEAM_ID_HEADER,
} from "./headers.js";
import { JsonObject, JsonValue } from "./types.js";

export class LogContext {
  attributes: JsonObject = {};

  static load(res: Response): LogContext {
    const existing = res.locals[EAVE_CTX_KEY];

    // Attach this context to the response object, if one wasn't already.
    if (existing) {
      return existing;
    }

    const ctx = new LogContext(res.req);
    res.locals[EAVE_CTX_KEY] = ctx;
    return ctx;
  }

  static wrap(ctx?: LogContext, req?: Request): LogContext {
    if (ctx) {
      return ctx;
    } else {
      return new LogContext(req);
    }
  }

  constructor(req?: Request) {
    if (req) {
      this.set({
        headers: getHeaders(req),
        eave_request_id: req.header(EAVE_REQUEST_ID_HEADER) || uuidv4(),
        eave_team_id: req.header(EAVE_TEAM_ID_HEADER),
        eave_account_id: req.header(EAVE_ACCOUNT_ID_HEADER),
        eave_origin: req.header(EAVE_ORIGIN_HEADER),
        request_path: req.originalUrl,
      });
    } else {
      this.set({
        eave_request_id: uuidv4(),
      });
    }
  }

  get eave_request_id(): string {
    return <string>this.attributes["eave_request_id"];
  }

  set eave_request_id(value: string) {
    this.set({ eave_request_id: value });
  }

  get eave_account_id(): string {
    return <string>this.attributes["eave_account_id"];
  }

  set eave_account_id(value: string) {
    this.set({ eave_account_id: value });
  }

  get eave_team_id(): string {
    return <string>this.attributes["eave_team_id"];
  }

  set eave_team_id(value: string) {
    this.set({ eave_team_id: value });
  }

  get eave_origin(): string {
    return <string>this.attributes["eave_origin"];
  }

  set eave_origin(value: string) {
    this.set({ eave_origin: value });
  }

  get feature_name(): string | undefined {
    return <string | undefined>this.attributes["feature_name"];
  }

  set feature_name(value: string | undefined) {
    this.set({ feature_name: value });
  }

  get(attribute: string): JsonValue | undefined {
    return this.attributes[attribute]
  }

  set(attributes: JsonObject): LogContext {
    Object.assign(this.attributes, attributes);
    return this;
  }
}

// class RequestFormatter {
//   transform(info: LogForm.TransformableInfo): LogForm.TransformableInfo | boolean {
//     const {
//       level,
//       message,
//       [LEVEL],
//       [MESSAGE],
//       [SPLAT],
//       ...rest
//     } = info;

//     const ctx = JSON.stringify(rest, null, 2);
//     return {
//       level,
//       message,
//       ctx,
//     };
//   };
// }

function createLogger(): winston.Logger {
  const level = sharedConfig.logLevel.toLowerCase();
  let logger: winston.Logger;

  /*
  There an issue logging errors that the winston maintainers seemingly have no interest in merging proposed fixes,
  so that leads us to needing two separate loggers for dev and production.
  GCP's Winston plugin does its own error formatting.
  https://github.com/winstonjs/logform/issues/100
  */
  if (sharedConfig.monitoringEnabled) {
    const loggingWinston = new LoggingWinston({ logName: "eave" });

    // LoggingWinston does its own formatting
    logger = winston.createLogger({
      level,
      transports: loggingWinston,
    });
  } else {
    const consoleTransport = new winston.transports.Console();

    logger = winston.createLogger({
      level,
      format: winston.format.combine(
        winston.format.simple(),
        // new RequestFormatter(),
        winston.format.colorize({
          all: true,
          colors: {
            debug: "grey",
            info: "blue",
            warn: "yellow",
            warning: "yellow",
            error: "red",
          },
        }),
      ),
      transports: consoleTransport,
    });
  }

  return logger;
}

class EaveLogger {
  rawLogger: winston.Logger;

  constructor() {
    this.rawLogger = createLogger();
  }

  debug(message: string, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.debug(message, this.makeExtra(...rest));
  }

  info(message: string, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.info(message, this.makeExtra(...rest));
  }

  warning(
    message: string | Error,
    ...rest: (JsonObject | LogContext | undefined)[]
  ) {
    let msg: string;
    if (message instanceof Error) {
      msg = message.stack || message.message;
    } else {
      msg = message;
    }

    this.rawLogger.warn(msg, this.makeExtra(...rest));
  }

  error(
    message: string | Error,
    ...rest: (JsonObject | LogContext | undefined)[]
  ) {
    let msg: string;
    if (message instanceof Error) {
      msg = message.stack || message.message;
    } else {
      msg = message;
    }

    this.rawLogger.error(msg, this.makeExtra(...rest));
  }

  exception(
    message: string | Error,
    ...rest: (JsonObject | LogContext | undefined)[]
  ) {
    this.error(message, ...rest);
  }

  critical(
    message: string | Error,
    ...rest: (JsonObject | LogContext | undefined)[]
  ) {
    this.error(message, ...rest);
  }

  private makeExtra(...rest: (JsonObject | LogContext | undefined)[]): {
    eave: JsonObject;
  } {
    return {
      eave: <JsonObject>rest.reduce((acc, cur) => {
        if (!cur) {
          return acc;
        }

        let attrs: JsonObject;
        if (cur instanceof LogContext) {
          attrs = cur.attributes;
        } else {
          attrs = cur;
        }

        return {
          ...acc,
          ...attrs,
        };
      }, {}),
    };
  }
}

export const eaveLogger = new EaveLogger();
