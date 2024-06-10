import { getAllEaveCookies } from "../cookies.js";
import { ScalarMap } from "../types.js";

export function getCorrelationContext() {
  const eaveCookies = getAllEaveCookies();
  const corrCtx: ScalarMap<string> = {};

  for (const [name, value] of eaveCookies) {
    corrCtx[name] = decodeURIComponent(value);
  }

  return corrCtx;
}
