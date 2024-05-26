import { eaveLogger } from "../logging.js";
import { JSONObject, JSONValue } from "../types.js";

export function safeJSONParse<T extends JSONValue>(value: string | null): T | null {
  if (value === null) {
    return null;
  }

  try {
    return JSON.parse(value);
  } catch (e) {
    eaveLogger.error(e);
    return null;
  }
}

export function compactJSONStringify(json: JSONValue): string {
  return JSON.stringify(json, undefined, 0); // 0 is default; being explicit because cookie size is important
}