import { logger } from "../internal/logging";
import { JsonValue } from "../types";

export function safeJSONParse<T extends JsonValue>(value: string | null): T | null {
  if (value === null) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch (e) {
    logger.error(e);
    return null;
  }
}

export function compactJSONStringify(json: JsonValue): string {
  return JSON.stringify(json, undefined, 0); // 0 is default; being explicit because cookie size is important
}
