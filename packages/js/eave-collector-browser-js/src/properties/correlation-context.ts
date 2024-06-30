import { getAllEaveCookies } from "../cookies";
import { ScalarMap } from "../types";

export function getCorrelationContext(): ScalarMap<string> {
  const eaveCookies = getAllEaveCookies();
  const corrCtx: ScalarMap<string> = {};

  for (const [name, value] of eaveCookies) {
    corrCtx[name] = decodeURIComponent(value);
  }

  return corrCtx;
}
