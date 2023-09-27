export function isHTTPError(httpResponse) {
  if (httpResponse.ok === false || httpResponse.status !== 200) {
    return true;
  }
  return false;
}
