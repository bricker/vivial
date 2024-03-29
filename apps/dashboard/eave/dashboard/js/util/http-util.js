export function isUnauthorized(httpResponse) {
  return httpResponse.status === 401;
}

export function isHTTPError(httpResponse) {
  return httpResponse.ok === false || httpResponse.status >= 400;
}

/**
 * Asynchronously logs the user out by redirecting to the logout page.
 */
export function logUserOut() {
  window.location.assign("/dashboard/logout");
}
