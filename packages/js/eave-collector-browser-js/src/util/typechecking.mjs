/**
 * Helper for typechecking
 *
 * @param {Node} node
 *
 * @returns {Element | null}
 */
export function castNodeToElement(node) {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {Element} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {Node} node
 *
 * @returns {HTMLElement | null}
 */
export function castNodeToHtmlElement(node) {
  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {HTMLElement} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {EventTarget | null} target
 *
 * @returns {HTMLElement | null}
 */
export function castEventTargetToHtmlElement(target) {
  if (!target) {
    return null;
  }

  // We're given an EventTarget, which is an interface implemented by many things, commonly Window or Node.
  // If this function is being called, then the caller should be pretty sure that the event target is an HTMLElement.
  // @ts-ignore
  const /** @type {Node} */ node = (target);

  if (node.nodeType === Node.ELEMENT_NODE) {
    const element = /** @type {HTMLElement} */ (node);
    return element;
  } else {
    return null;
  }
}

/**
 * Helper for typechecking
 *
 * @param {PerformanceEntry} entry
 *
 * @returns {PerformanceNavigationTiming | null}
 */
export function castPerformanceEntryToNavigationTiming(entry) {
  if (entry.entryType === "navigation") {
    const timing = /** @type {PerformanceNavigationTiming} */ (entry);
    return timing;
  } else {
    return null;
  }
}