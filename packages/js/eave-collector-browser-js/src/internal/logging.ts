


/*
debug, info, warn, error, critical functions

api call
use logger lib to console if debug mode
threaded queue?? not necessary since browser is serial/single user?

*/
class EaveLogger {
  tag: string;

  constructor() {
    this.tag = "[eave]";
  }

  debug(...args: any[]) {
    console.debug(this.tag, ...args)
  }

  info(...args: any[]) {
    console.log(this.tag, ...args)
  }

  warn(...args: any[]) {
    console.warn(this.tag, ...args)
  }

  error(...args: any[]) {
    console.error(this.tag, ...args)
  }

  critical(...args: any[]) {
    console.error(this.tag, ...args)
  }
}

export const logger = new EaveLogger();