import { LOG_TRACKER_URL, MODE } from "./compile-config";

type LogPayload = {
  name: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";
  msg: string;
};

class EaveLogger {
  tag: string;

  constructor() {
    this.tag = "collector-browser-js";
  }

  #send(logs: LogPayload[]) {
    try {
      const json = JSON.stringify({
        logs,
      });

      // Important note: The `type` property here should be `application/x-www-form-urlencoded`, because that mimetype is CORS-safelisted as documented here:
      // https://fetch.spec.whatwg.org/#cors-safelisted-request-header
      // If set to a non-safe mimetype (eg application/json), sendBeacon will send a pre-flight CORS request (OPTIONS) to the server, and the server is then responsible
      // for responding with CORS "access-control-allow-*" headers. That's okay, but it adds unnecessary overhead to both the client and the server.
      const blob = new Blob([json], {
        type: "application/x-www-form-urlencoded; charset=UTF-8",
      });

      // @ts-ignore: this is a known global variable implicitly set on the window.
      const clientId: string | undefined = window.EAVE_CLIENT_ID;

      console.debug("Sending logs", logs);

      const success = navigator.sendBeacon(`${LOG_TRACKER_URL}?clientId=${clientId}`, blob);

      if (!success) {
        console.warn("Failed to send logs.");
        return;
      }
    } catch (e) {
      console.error(e);
      return;
    }
  }

  #strjoin(args: any[]) {
    const builder: string[] = [];
    for (let i = 0; i < args.length; i++) {
      if (typeof args[i] === "string") {
        builder.push(args[i]);
      } else {
        builder.push(JSON.stringify(args[i]));
      }
    }
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
      console.log(this.tag, ...args);
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
