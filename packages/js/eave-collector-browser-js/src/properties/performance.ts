import { PerformanceProperties } from "../types";
import { castPerformanceEntryToNavigationTiming } from "../util/typechecking";

export function getPerformanceProperties(): PerformanceProperties | null {
  const entries = performance.getEntriesByType("navigation");

  // For PerformanceNavigationTiming, only the current document is included, so there is only one entry.
  // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming
  const entry = entries[0];
  if (!entry) {
    return null;
  }

  const timing = castPerformanceEntryToNavigationTiming(entry);
  if (!timing) {
    return null;
  }

  return {
    network_latency_ms: timing.responseEnd,
    dom_load_latency_ms: timing.domComplete,
  };
}
