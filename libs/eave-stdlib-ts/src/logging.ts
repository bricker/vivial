import winston from 'winston';
import { LoggingWinston as CloudLoggingTransport } from '@google-cloud/logging-winston';
import { sharedConfig } from './config';

const logger = winston.createLogger({
  level: sharedConfig.logLevel,
  transports: [
    new winston.transports.Console(),
  ],
});

if (sharedConfig.monitoringEnabled) {
  logger.add(new CloudLoggingTransport());
}

export default logger;
