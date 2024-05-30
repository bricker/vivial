import { EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE } from "./internal/js-events";
import { StringMap } from "./types";

export const COOKIE_NAME_PREFIX = "_eave.";
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
export function setEaveCookie({
  name,
  value,
  maxAgeSeconds,
  expires,
  path = "/",
  domain,
  isSecure = true,
  sameSite = "Lax",
}: {
  name: string;
  value: string;
  maxAgeSeconds?: number;
  expires?: Date;
  path?: string;
  domain?: string;
  isSecure?: boolean;
  sameSite?: "None" | "Lax" | "Strict";
}) {
  const cookieAttrs: [string, string | true][] = [[name, encodeURIComponent(value)]];

  if (maxAgeSeconds !== undefined) {
    cookieAttrs.push(["Max-Age", `${maxAgeSeconds}`]);
  }

  if (expires !== undefined) {
    cookieAttrs.push(["Expires", expires.toUTCString()]);
  }

  cookieAttrs.push(["Path", path]);

  if (!domain) {
    const url = new URL(window.location.href);
    domain = url.hostname;
  }

  cookieAttrs.push(["Domain", domain]);
  cookieAttrs.push(["SameSite", sameSite]);

  if (sameSite === "None") {
    // SameSite None cookies must also be Secure, per spec
    isSecure = true;
  }

  if (isSecure) {
    cookieAttrs.push(["Secure", true]);
  }

  const cookieValue = cookieAttrs
    .map(([attrName, attrValue]) => (attrValue === true ? `${attrName}` : `${attrName}=${attrValue}`))
    .join(";");
  document.cookie = cookieValue;
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
