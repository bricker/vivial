import { myWindow } from "../types.js";

export interface HTTPResponse {
  status: number;
  ok: boolean;
}

export function isUnauthorized(httpResponse: HTTPResponse): boolean {
  return httpResponse.status === 401;
}

export function isHTTPError(httpResponse: HTTPResponse): boolean {
  return httpResponse.ok === false || httpResponse.status >= 400;
}

/**
 * Asynchronously logs the user out by redirecting to the logout page.
 */
export function logUserOut(): void {
  window.location.assign("/logout");
}

export const GRAPHQL_API_BASE = `${myWindow.app.apiBase}/graphql`;
