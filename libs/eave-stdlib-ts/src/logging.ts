import { Logging, SeverityNames } from '@google-cloud/logging';
import { sharedConfig } from './config.js';

// This module defines some basic functionality for switching between console and Cloud Logger, depending on environment.
// Winston is a more robust solution, but has many dependencies and doesn't play nicely with the Forge runtime environment.

enum LogLevel {
  debug = 0,
  info = 1,
  warn = 2,
  error = 3,
}

type LogLevelNames = 'debug' | 'info' | 'warn' | 'error';

const LOG_LEVEL_TO_NAME: {[key:number]: LogLevelNames} = {
  [LogLevel.debug]: 'debug',
  [LogLevel.info]: 'info',
  [LogLevel.warn]: 'warn',
  [LogLevel.error]: 'error',
};

const LOG_LEVEL_TO_GCP_SEVERITY_NAME: {[key:number]: SeverityNames} = {
  [LogLevel.debug]: 'debug',
  [LogLevel.info]: 'info',
  [LogLevel.warn]: 'warning',
  [LogLevel.error]: 'error',
};

const NAME_TO_LOG_LEVEL: {[key:string]: LogLevel} = {
  debug: LogLevel.debug,
  info: LogLevel.info,
  warn: LogLevel.warn,
  error: LogLevel.error,
};

interface Transport {
  log: (level: LogLevel, data: any, metadata?: {[key:string]: any}) => void;
}

class ConsoleTransport implements Transport {
  log(level: LogLevel, data: any, metadata?: {[key:string]: any}) {
    const severity: LogLevelNames = LOG_LEVEL_TO_NAME[level] || 'info';

    if (typeof data === 'string') {
      console[severity](data, metadata);
    } else if (data['message'] !== undefined) {
      console[severity](data['message'], metadata);
      console.dir(data, { depth: null });
    } else {
      console.dir(data, { depth: null });
    }
  }
}

class CloudLoggingTransport implements Transport {
  cloudLogger: Logging;

  constructor() {
    this.cloudLogger = new Logging();
  }

  log(level: LogLevel, data: any, metadata?: {[key:string]: any}) {
    const log = this.cloudLogger.log('eave');
    const severity: SeverityNames = LOG_LEVEL_TO_GCP_SEVERITY_NAME[level] || 'info';

    const metadataNormalized = metadata || {};
    metadataNormalized['severity'] = severity.toUpperCase();
    const entry = log.entry(metadataNormalized, data);
    // This is an async function, intentionally not being awaited
    log.write(entry);
  }
}

class EaveLogger {
  level: LogLevel;

  transport: Transport;

  constructor(level: LogLevel = LogLevel.info) {
    this.level = level;
    this.transport = new ConsoleTransport();
  }

  debug(data: any, metadata?: {[key:string]: any}) {
    if (this.level > LogLevel.debug) {
      return;
    }

    this.transport.log(LogLevel.debug, data, metadata);
  }

  info(data: any, metadata?: {[key:string]: any}) {
    if (this.level > LogLevel.info) {
      return;
    }
    this.transport.log(LogLevel.info, data, metadata);
  }

  warning(data: any, metadata?: {[key:string]: any}) {
    if (this.level > LogLevel.warn) {
      return;
    }
    this.transport.log(LogLevel.warn, data, metadata);
  }

  error(data: any, metadata?: {[key:string]: any}) {
    if (this.level > LogLevel.error) {
      return;
    }
    this.transport.log(LogLevel.error, data, metadata);
  }
}

function createLogger() {
  const logLevel = NAME_TO_LOG_LEVEL[sharedConfig.logLevel.toLowerCase()] || LogLevel.info;
  const logger = new EaveLogger(logLevel);

  if (sharedConfig.monitoringEnabled) {
    // prod
    // Overwrite the default console logger
    logger.transport = new CloudLoggingTransport();
  }

  return logger;
}

export default createLogger();
