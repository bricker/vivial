import { sendWithClientId } from "../send";
import { LogPayload, Mode } from "./types";

export class EaveLogger {
  tag: string;
  logIngestUrl: string;
  mode: Mode;
  clientId: string;

  constructor({
    tag,
    logIngestUrl,
    mode,
    clientId,
  }: {
    tag: string;
    logIngestUrl: string;
    mode: Mode;
    clientId: string;
  }) {
    this.tag = tag;
    this.logIngestUrl = logIngestUrl;
    this.mode = mode;
    this.clientId = clientId;
  }

  #send(logs: LogPayload[]) {
    sendWithClientId({ jsonBody: { logs }, url: this.logIngestUrl, clientId: this.clientId });
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
    if (this.mode !== "production") {
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
    if (this.mode !== "production") {
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
    if (this.mode !== "production") {
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
    if (this.mode !== "production") {
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
    if (this.mode !== "production") {
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
