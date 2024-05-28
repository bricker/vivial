import { LOG_LEVEL } from "./internal/compile-config";
import { LogLevel } from "./types";

/**
 * Wrapper functions to prepend the "[eave]" tag to logs.
 */

const LOG_TAG = "[eave]";

const LOG_LEVELS = Object.freeze({
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  SILENT: 99,
});

class EaveLogger {
  #level: LogLevel = "INFO";

  #internalLogger = console;

  constructor(level?: LogLevel) {
    if (level) {
      this.level = level
    }
  }

  get level(): LogLevel {
    return this.#level;
  }

  set level(level: LogLevel) {
    this.#level = level;
  }

  get #levelInt(): number {
    const levelInt = LOG_LEVELS[this.level];

    // It may seem like `levelInt` will never be undefined, but remember that this code is transpiled to javascript
    // and nothing else at runtime checks that the log level passed into this class is valid.

    // do comparison to `undefined` because #levelInt may be 0, a falsey value in javascript
    return levelInt === undefined ? LOG_LEVELS.INFO : levelInt;
  }

  debug(...messages: any[]) {
    if (this.#levelInt <= LOG_LEVELS.DEBUG) {
      this.#internalLogger.debug(LOG_TAG, ...messages);
    }
  }

  info(...messages: any[]) {
    if (this.#levelInt <= LOG_LEVELS.INFO) {
      this.#internalLogger.info(LOG_TAG, ...messages);
    }
  }

  warn(...messages: any[]) {
    if (this.#levelInt <= LOG_LEVELS.WARN) {
      this.#internalLogger.warn(LOG_TAG, ...messages);
    }
  }

  error(...messages: any[]) {
    if (this.#levelInt <= LOG_LEVELS.ERROR) {
      this.#internalLogger.error(LOG_TAG, ...messages);
    }
  }
}

export const eaveLogger = new EaveLogger(LOG_LEVEL);