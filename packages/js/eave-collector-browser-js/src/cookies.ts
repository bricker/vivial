export const COOKIE_NAME_PREFIX = "_eave.";
export const ENCRYPTED_COOKIE_PREFIX = `${COOKIE_NAME_PREFIX}nc.`;
export const ENCRYPTED_ACCOUNT_COOKIE_PREFIX = `${ENCRYPTED_COOKIE_PREFIX}act.`;
export const TRAFFIC_SOURCE_COOKIE_NAME = `${COOKIE_NAME_PREFIX}traffic_source`;
export const SESSION_COOKIE_NAME = `${COOKIE_NAME_PREFIX}session`;
export const SESSION_LENGTH_MAX_AGE_SEC = 30 * 60;
export const TRAFFIC_SOURCE_COOKIE_MAX_AGE_SEC = SESSION_LENGTH_MAX_AGE_SEC;
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
 * Get all Eave-managed cookies, except consent cookies.
 */
export function getAllEaveCookies(): URLSearchParams {
  const allCookies = getAllCookies();
  const eaveCookies = new URLSearchParams();

  for (const [name, value] of allCookies) {
    if (name.startsWith(COOKIE_NAME_PREFIX)) {
      eaveCookies.append(name, value);
    }
  }

  return eaveCookies;
}

/**
 * Get all Eave-managed account cookies
 */
export function getAllEaveAccountCookies(): URLSearchParams {
  const allCookies = getAllCookies();
  const accountCookies = new URLSearchParams();

  for (const [name, value] of allCookies) {
    if (name.startsWith(ENCRYPTED_ACCOUNT_COOKIE_PREFIX)) {
      accountCookies.append(name, value);
    }
  }

  return accountCookies;
}

/**
 * Get a cookie
 */
export function getCookie(name: string): string | null {
  const cookies = getAllCookies();
  const cookie = cookies.get(name);
  return cookie ? decodeURIComponent(cookie) : null;
}

/**
 * https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie
 */
export function setCookie({
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

  // https://publicsuffix.org/list/public_suffix_list.dat
  if (!domain) {
    // FIXME: This _does not work_ for many domains, eg .co.uk domains.
    // The public suffix list should be used.
    // See EAVE-201
    const url = new URL(window.location.href);
    const parts = url.hostname.split(".");
    domain = parts.slice(-2).join(".");
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
export function deleteCookie(args: { name: string; path?: string; domain?: string }) {
  setCookie({
    ...args,
    value: "",
    expires: new Date(0),
  });
}

/**
 * Delete all Eave-managed cookies, except consent cookies
 */
export function deleteAllEaveCookies() {
  const allEaveCookies = getAllEaveCookies();

  for (const [name, _] of allEaveCookies) {
    deleteCookie({ name });
  }
}

export function cookiesEventHandler(_evt: Event) {
  deleteAllEaveCookies();
}
