import { getAllEaveCookies } from "../cookies";
import { ScalarMap } from "../types";

export function getCorrelationContext() {
  const eaveCookies = getAllEaveCookies();
  const corrCtx: ScalarMap<string> = {};

  for (const [name, value] of eaveCookies) {
    corrCtx[name] = decodeURIComponent(value);
  }

  return corrCtx;
}
