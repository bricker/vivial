import { sendBeaconWithEaveAuth } from "./beacon";
import { LOG_TRACKER_URL, MODE } from "./compile-config";

type LogPayload = {
  name: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";
  msg: string;
};

class EaveLogger {
  tag: string;

  constructor() {
    this.tag = "eave-collector-browser-js";
  }

  #send(logs: LogPayload[]) {
    sendBeaconWithEaveAuth({ jsonBody: { logs }, url: LOG_TRACKER_URL });
  }

  #strjoin(args: any[]) {
    const builder: string[] = args.map((arg) => {
      if (typeof arg === "string") {
        return arg;
      } else {
        return JSON.stringify(arg);
      }
    });
    return builder.join(" ");
  }

  debug(...args: any[]) {
    if (MODE !== "production") {
      console.debug(this.tag, ...args);
    }
    this.#send([
      {
        name: this.tag,
        level: "DEBUG",
        msg: this.#strjoin(args),
      },
    ]);
  }

  info(...args: any[]) {
    if (MODE !== "production") {
      console.info(this.tag, ...args);
    }
    this.#send([
      {
        name: this.tag,
        level: "INFO",
        msg: this.#strjoin(args),
      },
    ]);
  }

  warn(...args: any[]) {
    if (MODE !== "production") {
      console.warn(this.tag, ...args);
    }
    this.#send([
      {
        name: this.tag,
        level: "WARN",
        msg: this.#strjoin(args),
      },
    ]);
  }

  error(...args: any[]) {
    if (MODE !== "production") {
      console.error(this.tag, ...args);
    }
    this.#send([
      {
        name: this.tag,
        level: "ERROR",
        msg: this.#strjoin(args),
      },
    ]);
  }

  critical(...args: any[]) {
    if (MODE !== "production") {
      console.error(this.tag, ...args);
    }
    this.#send([
      {
        name: this.tag,
        level: "CRITICAL",
        msg: this.#strjoin(args),
      },
    ]);
  }
}

export const logger = new EaveLogger();
