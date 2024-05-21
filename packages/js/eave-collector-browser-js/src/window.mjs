/**
 * Returns the current url of the page that is currently being visited.
 *
 * @returns {string}
 */
export function getCurrentUrl() {
  return new URL(window.location.href);
}
