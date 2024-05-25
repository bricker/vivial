// @ts-check

import { LOG_LEVEL } from "./compile-config.mjs";

/**
 * Wrapper functions to prepend the "[eave]" tag to logs.
 */

const LOG_TAG = "[eave]";

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  SILENT: 99,
}

class EaveLogger {
  /** @type {string} */
  #level = "INFO";

  /** @type {Console} */
  #internalLogger = console;

  /**
   * @param {string} [level]
   *
   * @noreturn
   */
  constructor(level) {
    if (level) {
      this.level = level
    }
  }

  get level() {
    return this.#level;
  }

  set level(level) {
    this.#level = level.toUpperCase();
  }

  get #levelInt() {
    const levelInt = LOG_LEVELS[this.level];
    if (levelInt === undefined) { // use undefined comparison because #levelInt may be 0, a falsey value in javascript
      return LOG_LEVELS.INFO;
    } else {
      return levelInt;
    }
  }

  /**
   * @param {any[]} messages
   */
  debug(...messages) {
    if (this.#levelInt <= LOG_LEVELS.DEBUG) {
      this.#internalLogger.debug(LOG_TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  info(...messages) {
    if (this.#levelInt <= LOG_LEVELS.INFO) {
      this.#internalLogger.info(LOG_TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  warn(...messages) {
    if (this.#levelInt <= LOG_LEVELS.WARN) {
      this.#internalLogger.warn(LOG_TAG, ...messages);
    }
  }

  /**
   * @param {any[]} messages
   */
  error(...messages) {
    if (this.#levelInt <= LOG_LEVELS.ERROR) {
      this.#internalLogger.error(LOG_TAG, ...messages);
    }
  }
}

export const eaveLogger = new EaveLogger(LOG_LEVEL);