import { URLSearchParams } from "url";
import { EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE } from "./internal/js-events.js";
import { StringMap } from "./types.js";
import { eaveLogger } from "./logging.js";

export const COOKIE_NAME_PREFIX = "eave.";
export const MAX_ALLOWED_COOKIE_AGE_SEC = 60 * 60 * 24 * 400; // 400 days (maximum allowed value in Chrome)


/**
 * Get all first-party cookies
 */
function getAllCookies(): URLSearchParams {
  const urlParamifiedCookies = document.cookie.replace(/; */g, "&");
  const cookies = new URLSearchParams(urlParamifiedCookies);
  return cookies;
}

/**
 * Get an Eave-managed cookie
 */
export function getEaveCookie(name: string): string | null {
  const cookies = getAllCookies();
  const cookie = cookies.get(name);
  return cookie ? decodeURIComponent(cookie) : null;
}

/**
 * Set an Eave-managed cookie
 * https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie
 */
export function setEaveCookie(
  { name, value, maxAgeSeconds, expires, path = "/", domain, isSecure = true, sameSite = "Lax"}:
  { name: string;
    value: string;
    maxAgeSeconds?: number;
    expires?: Date;
    path?: string;
    domain?: string;
    isSecure?: boolean;
    sameSite?: "None" | "Lax" | "Strict";
  }
) {
  if (!sameSite) {
    sameSite = "Lax";
  }

  if (sameSite === "None") {
    // SameSite None cookies must also be Secure, per spec
    isSecure = true;
  }

  const cookieAttrs: [string, string | boolean][] = [[name, encodeURIComponent(value)]];

  if (maxAgeSeconds !== undefined) {
    cookieAttrs.push(["max-age", `${maxAgeSeconds}`]);
  }

  if (expires !== undefined) {
    cookieAttrs.push(["expires", expires.toUTCString()]);
  }

  cookieAttrs.push(["path", path || "/"]);

  if (domain) {
    cookieAttrs.push(["domain", domain]);
  }

  cookieAttrs.push(["SameSite", sameSite || "Lax"]);

  if (sameSite === "None") {
    // SameSite None cookies must also be Secure, per spec
    isSecure = true;
  }

  if (isSecure === undefined) {
    isSecure = true;
  }

  if (isSecure) {
    cookieAttrs.push(["secure", true]);
  }

  document.cookie = cookieAttrs.map(([cookieName, cookieValue]) => cookieValue === true ? `${cookieName}` : `${cookieName}=${cookieValue}`).join(";");
}


/**
 * Delete an Eave-managed cookie
 */
export function deleteEaveCookie(args: { name: string; path?: string; domain?: string }) {
  setEaveCookie({
    ...args,
    value: "",
    expires: new Date(0),
  });
}


/**
 * Delete all Eave-managed cookies, except consent cookies
 */
export function deleteAllEaveCookies() {
  const allCookies = getAllCookies();

  for (const [name, _] of allCookies) {
    if (name.startsWith(COOKIE_NAME_PREFIX)) {
      deleteEaveCookie({ name });
    }
  }
}

/**
 * Get all Eave-managed cookies, except consent cookies
 *
 * NOTE: Although there may be multiple cookies with the same name (as mentioned in https://www.rfc-editor.org/rfc/rfc6265, for example),
 * this function assumes cookie names are unique. However, because this function only returns Eave-managed cookies, we can be reasonably sure that the names are unique.
 * The primary reason for returning a map instead of an array of arrays is for simpler table schemas and querying in the dashboards.
 *
 * @returns a map of cookie name -> value.
 */
export function getAllEaveCookies() {
  const allCookies = getAllCookies();

  const eaveCookies: StringMap<string> = {};

  for (const [cookieName, cookieValue] of allCookies) {
    if (cookieName.startsWith(COOKIE_NAME_PREFIX)) {
      eaveCookies[cookieName] = cookieValue;
    }
  }

  return eaveCookies;
}

function handleEvent(_evt: Event) {
  deleteAllEaveCookies();
}

let initialized = false;

/**
 * Register event listeners. Call this only once, when the page loads.
 */
export function initializeCookieModule() {
  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    window.addEventListener(EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE, handleEvent, { passive: true });
  }

  initialized = true;
}