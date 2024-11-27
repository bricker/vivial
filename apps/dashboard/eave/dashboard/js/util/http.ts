import { myWindow } from "../types/window";

/**
 * Asynchronously logs the user out by redirecting to the logout page.
 */
export function logUserOut(): void {
  window.location.assign("/logout");
}

export const CORE_API_BASE = myWindow.app.apiBase;
export const GRAPHQL_API_BASE = `${CORE_API_BASE}/graphql`;
