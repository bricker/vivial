// @ts-check

/**
 * Wrapper functions to prepend the "[eave]" tag to logs.
 */

const TAG = "[eave]";

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  SILENT: 99,
}

// @ts-ignore - LOG_LEVEL is defined by Webpack config during compilation
let LOG_LEVEL_INT = LOG_LEVELS[LOG_LEVEL.toUpperCase()]; // eslint-disable-line no-undef
if (LOG_LEVEL_INT === undefined) {
  LOG_LEVEL_INT = LOG_LEVELS.INFO;
}

class EaveLogger {
  /** @type {Console} */
  #internalLogger = console;

  /**
   * @param {any[]} messages
   */
  debug(...messages) {
    if (LOG_LEVEL_INT <= LOG_LEVELS.DEBUG) {
      this.#internalLogger.debug(TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  info(...messages) {
    if (LOG_LEVEL_INT <= LOG_LEVELS.INFO) {
      this.#internalLogger.info(TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  warn(...messages) {
    if (LOG_LEVEL_INT <= LOG_LEVELS.WARN) {
      this.#internalLogger.warn(TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  error(...messages) {
    if (LOG_LEVEL_INT <= LOG_LEVELS.ERROR) {
      this.#internalLogger.error(TAG, ...messages);
    }
  }
}

export const eaveLogger = new EaveLogger();