export function isHTTPError(httpResponse) {
  return httpResponse.ok === false || httpResponse.status >= 400;
}
