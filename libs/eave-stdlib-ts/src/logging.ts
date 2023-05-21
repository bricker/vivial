import winston from 'winston';
import { LoggingWinston as CloudLoggingTransport } from '@google-cloud/logging-winston';
import { sharedConfig } from './config.js';

const logger = winston.createLogger({
  level: sharedConfig.logLevel,
});

if (sharedConfig.monitoringEnabled) {
  // prod
  logger.add(new CloudLoggingTransport());
} else {
  // dev
  logger.add(new winston.transports.Console());
}

export default logger;
