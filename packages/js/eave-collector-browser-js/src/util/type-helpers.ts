import { KeyValueArray, NullableStringMap, StringMap } from "../types.js";

/**
 * Helper for typechecking
 */
export function castNodeToElement(node: Node): Element | null {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = node as Element;
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 */
export function castNodeToHtmlElement(node: Node): HTMLElement | null {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = node as HTMLElement;
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 */
export function castEventTargetToHtmlElement(target: EventTarget): HTMLElement | null {
  if (!target) {
    return null;
  }

  const node = target as Node;

  if (node.nodeType === Node.ELEMENT_NODE) {
    // We're given an EventTarget, which is an interface implemented by many things, commonly Window or Node.
    // If this function is being called, then the caller should be pretty sure that the event target is an HTMLElement.
    const element = node as HTMLElement;
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 */
export function castPerformanceEntryToNavigationTiming(entry: PerformanceEntry): PerformanceNavigationTiming | null {
  if (entry.entryType === "navigation") {
    const timing = entry as PerformanceNavigationTiming;
    return timing;
  } else {
    return null;
  }
}

export function toKeyValueArray(map: NullableStringMap<string>): KeyValueArray {
  return Object.entries(map).map(([key, value]) => ({ key, value }));
}

export function pairsToKeyValueArray(pairs: [string, string][]): KeyValueArray {
  return pairs.map(([key, value]) => ({ key, value }));
}