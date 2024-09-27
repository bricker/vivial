export type LogPayload = {
  name: string;
  level: "DEBUG" | "INFO" | "WARN" | "ERROR" | "CRITICAL";
  msg: string;
};

export type Logger = {
  debug: (...args: any[]) => void;
  info: (...args: any[]) => void;
  warn: (...args: any[]) => void;
  error: (...args: any[]) => void;
};

export type Mode = "production" | "development";
