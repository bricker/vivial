// @ts-check

import { COOKIE_CONSENT_REVOKED_EVENT_TYPE } from "../internal/event-types.mjs";
import * as Types from "../types.mjs"; // eslint-disable-line no-unused-vars

export const COOKIE_NAME_PREFIX = "eave.";

/**
 * CookieManager class
 */
class CookieManager {
  constructor() {
    window.addEventListener(COOKIE_CONSENT_REVOKED_EVENT_TYPE, this);
  }

  /**
   * Interface for EventTarget.dispatchEvent()
   *
   * @param {Event} event
   *
   * @noreturn
   */
  handleEvent(event) {
    switch (event.type) {
      case COOKIE_CONSENT_REVOKED_EVENT_TYPE:
        this.deleteEaveCookies();
        break;
      default:
        break;
    }
  }

  /**
   * Get cookie value
   *
   * @param {string} name
   *
   * @returns {string | undefined} cookie value for `configCookieNamePrefix`+`cookieName` or 0 if not found
   */
  getCookie(name) {
    const cookies = this.#getAllCookies();
    const cookie = cookies.get(name);
    return cookie ? decodeURIComponent(cookie) : undefined;
  }

  /**
   * Set cookie value
   *
   * @param {object} args
   * @param {string} args.name base name to set cookie for. Actual cookie set at `configCookieNamePrefix`+`cookieName`
   * @param {string} args.value
   * @param {Date} [args.expires] (optional)
   * @param {number} [args.maxAgeSeconds] (optional)
   * @param {string | null} [args.path="/"] site path to limit cookie sharing to (default "/")
   * @param {string} [args.domain] domain to limit cookie sharing to (optional)
   * @param {boolean} [args.isSecure=true] whether cookie is only attached to https requests (default falsey)
   * @param {string} [args.sameSite="Lax"] cookie sharing restrictions (default "Lax")
   *    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
   *
   * @noreturn
   */
  setCookie({ name, value, maxAgeSeconds, expires, path, domain, isSecure, sameSite }) {
    if (!sameSite) {
      sameSite = "Lax";
    }

    if (sameSite === "None") {
      // SameSite None cookies must also be Secure, per spec
      isSecure = true;
    }

    const /** @type {[string,string | null][]} */ cookieAttrs = [[name, encodeURIComponent(value)]];

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
      cookieAttrs.push(["secure", null]);
    }

    document.cookie = cookieAttrs.map(([key, value]) => value ? `${key}=${value}` : `${value}`).join(";");
  }

  /**
   * Gets all cookies with the `configCookieNamePrefix` prefix; a.k.a the ones Eave manages
   *
   * @returns {string[][]} list of eave cookie key/value pairs, ["cookieName", "cookieValue"]
   */
  getEaveCookies() {
    const allCookies = this.#getAllCookies();
    const /** @type {[string, string][]} */ eaveCookies = [];

    for (const [cookieName, cookieValue] of allCookies) {
      if (cookieName.startsWith(COOKIE_NAME_PREFIX)) {
        eaveCookies.push([cookieName, cookieValue]);
      }
    }

    return eaveCookies;
  }

  /**
   * Deletes all cookies with the `configCookieNamePrefix` prefix; a.k.a the ones Eave manages
   *
   * @noreturn
   */
  deleteEaveCookies() {
    var savedConfigCookiesDisabled = this.configCookiesDisabled;

    // Temporarily allow cookies just to delete the existing ones
    this.configCookiesDisabled = false;

    for (const [cookieName, _] of this.getEaveCookies()) {
      this.deleteCookie({
        name: cookieName,
      });
    }

    this.configCookiesDisabled = savedConfigCookiesDisabled;
  }

  /**
   * Delete a first-party Eave cookie
   * Since we delete via `this.setCookie`, `cookieName` will automatically be prefixed
   * with `configCookieNamePrefix`.
   *
   * @param {object} args
   * @param {string} args.name
   * @param {string} [args.path="/"]
   * @param {string} [args.domain]
   *
   * @noreturn
   */
  deleteCookie({ name, path, domain }) {
    this.setCookie({
      name,
      value: "",
      expires: new Date(0),
      path,
      domain,
    });
  }

  /**
   * @returns {URLSearchParams}
   */
  #getAllCookies() {
    const urlParamifiedCookies = document.cookie.replace(/; */g, "&");
    const cookies = new URLSearchParams(urlParamifiedCookies);
    return cookies;
  }
}

export const cookieManager = new CookieManager();