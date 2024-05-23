/**
 * Wrapper functions to prepend the "[eave]" tag to logs.
 */

const TAG = "[eave]";

class EaveLogger {
  /** @type {Console} */
  #internalLogger = console;

  /**
   * @param {any[]} messages
   */
  debug(...messages) {
    this.#internalLogger.debug(TAG, ...messages);
  }

  /**
   * @param {any[]} messages
   */
  info(...messages) {
    this.#internalLogger.info(TAG, ...messages);
  }

  /**
   * @param {any[]} messages
   */
  warn(...messages) {
    this.#internalLogger.warn(TAG, ...messages);
  }

  /**
   * @param {any[]} messages
   */
  error(...messages) {
    this.#internalLogger.error(TAG, ...messages);
  }
}

export const eaveLogger = new EaveLogger();
