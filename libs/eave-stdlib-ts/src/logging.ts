import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';
import lf from 'logform';
import { LoggingWinston } from '@google-cloud/logging-winston';
import { sharedConfig } from './config.js';
import { JsonObject, JsonValue } from './types.js';
import { Request } from 'express';
import headers from './headers.js';

export class LogContext {
  attributes: JsonObject = {};

  static wrap(ctx?: LogContext): LogContext {
    if (ctx) {
      return ctx;
    } else {
      return new LogContext();
    }
  }

  constructor(req?: Request) {
    const requestId = req?.header(headers.EAVE_REQUEST_ID_HEADER) || uuidv4();
    this.set({ request_id: requestId });
  }

  get request_id(): string {
    return <string> this.attributes['request_id'];
  }

  set(attributes: JsonObject): LogContext {
    Object.assign(this.attributes, attributes);
    return this;
  }
}

const customErrorFormatter = winston.format((info: lf.TransformableInfo, _opts?: any): lf.TransformableInfo | boolean => {
  if (info instanceof Error) {
    // Example: logger.error(e)
    // eslint-disable-next-line no-param-reassign
    info.message = info['stack'];
  } else if (info.message instanceof Error) {
    // Example: logger.error(e, { additionalContext: '123' })
    // eslint-disable-next-line no-param-reassign
    info.message = info.message['stack'];
  }

  return info;
});

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
    const loggingWinston = new LoggingWinston({ logName: 'eave' });

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
        customErrorFormatter(),
        winston.format.simple(),
        winston.format.colorize({
          all: true,
          colors: {
            debug: 'grey',
            info: 'blue',
            warn: 'yellow',
            warning: 'yellow',
            error: 'red',
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

  debug(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.debug({
      message,
      ...this.makeExtra(...rest),
    });
  }

  info(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.info({
      message,
      ...this.makeExtra(...rest),
    });
  }

  warning(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.warning({
      message,
      ...this.makeExtra(...rest),
    });
  }

  error(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.error({
      message,
      ...this.makeExtra(...rest),
    });
  }

  exception(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.error({
      message,
      ...this.makeExtra(...rest),
    });
  }

  critical(message: string | Error, ...rest: (JsonObject | LogContext | undefined)[]) {
    this.rawLogger.error({
      message,
      ...this.makeExtra(...rest),
    });
  }

  private makeExtra(...rest: (JsonObject | LogContext | undefined)[]): { eave: JsonObject } {
    return {
      eave: <JsonObject>rest.reduce((cur, acc) => {
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

export default new EaveLogger();
