import winston from 'winston';
import lf from 'logform';
import { LoggingWinston } from '@google-cloud/logging-winston';
import { sharedConfig } from './config.js';

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
  const logLevel = sharedConfig.logLevel.toLowerCase();
  let logger: winston.Logger;

  /*
  There an issue logging errors that the winston maintainers seemingly have no interest in merging proposed fixes,
  so that leads us to needing two separate loggers for dev and production.
  GCP's Winston plugin does its own error formatting.
  https://github.com/winstonjs/logform/issues/100
  */
  if (sharedConfig.monitoringEnabled) {
    const loggingWinston = new LoggingWinston({ logName: 'eave' });

    logger = winston.createLogger({
      level: logLevel,
      transports: loggingWinston,
    });
  } else {
    const consoleTransport = new winston.transports.Console();

    logger = winston.createLogger({
      level: logLevel,
      format: winston.format.combine(
        customErrorFormatter(),
        winston.format.simple(),
        winston.format.colorize({
          all: true,
          colors: {
            debug: 'grey',
            info: 'blue',
            warn: 'yellow',
            error: 'red',
          },
        }),
      ),
      transports: consoleTransport,
    });
  }

  return logger;
}

export default createLogger();
