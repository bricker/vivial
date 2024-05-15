// @ts-check

import "./globals.mjs";
import * as h from "./helpers.mjs";

/**
 * CookieManager class
 */
export class CookieManager {
  constructor() {
    this.SESSION_ID_COOKIE_NAME = "session_id";
    this.VISITOR_ID_COOKIE_NAME = "visitor_id";
    this.CONSENT_COOKIE_NAME = "consent";
    this.COOKIE_CONSENT_COOKIE_NAME = "cookie_consent";
    this.CONSENT_REMOVED_COOKIE_NAME = "consent_removed";
    // First-party cookie name prefix
    this.configCookieNamePrefix = "_eave_";
    // Life of the visitor cookie (in milliseconds)
    this.configVisitorCookieTimeout = 33955200000; // 13 months (365 days + 28days)
    // Life of the session cookie (in milliseconds)
    this.configSessionCookieTimeout = 1800000; // 30 minutes
    // Life of the referral cookie (in milliseconds)
    this.configReferralCookieTimeout = 15768000000; // 6 months
    // First-party cookie domain
    // User agent defaults to origin hostname
    this.configCookieDomain = undefined;
    // First-party cookie path
    // Default is user agent defined.
    this.configCookiePath = undefined;
    // Whether to use "Secure" cookies that only work over SSL
    this.configCookieIsSecure = false;
    // Set SameSite attribute for cookies
    this.configCookieSameSite = "Lax";
    // First-party cookies are disabled
    this.configCookiesDisabled = false;
  }

  /**
   * Prefix `cookieName` with `configCookieNamePrefix` if it has not been prefixed already
   *
   * @param {string} cookieName
   * @returns {string}
   */
  #getCookieName(cookieName) {
    if (!cookieName.startsWith(this.configCookieNamePrefix)) {
      return this.configCookieNamePrefix + cookieName;
    }
    return cookieName;
  }

  /**
   * Get cookie value
   *
   * @param {string} name
   * @returns {string | undefined} cookie value for `configCookieNamePrefix`+`cookieName` or 0 if not found
   */
  getCookie(name) {
    const cookieName = this.#getCookieName(name);
    if (
      this.configCookiesDisabled &&
      cookieName !== this.#getCookieName(this.CONSENT_REMOVED_COOKIE_NAME)
    ) {
      return;
    }

    var cookiePattern = new RegExp("(^|;)[ ]*" + cookieName + "=([^;]*)"),
      cookieMatch = cookiePattern.exec(document.cookie);

    return cookieMatch ? decodeURIComponent(cookieMatch[2]) : undefined;
  }

  /**
   * Set cookie value
   *
   * @param {string} name base name to set cookie for. Actual cookie set at `configCookieNamePrefix`+`cookieName`
   * @param {string} value
   * @param {number} [msToExpire] (optional)
   * @param {string | null} [path="/"] site path to limit cookie sharing to (default "/")
   * @param {string} [domain] domain to limit cookie sharing to (optional)
   * @param {boolean} [isSecure] whether cookie is only attached to https requests (default falsey)
   * @param {string} [sameSite] cookie sharing restrictions (default "Lax")
   *    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
   * @noreturn
   */
  setCookie(name, value, msToExpire, path, domain, isSecure, sameSite) {
    const cookieName = this.#getCookieName(name);
    if (
      this.configCookiesDisabled &&
      cookieName !== this.#getCookieName(this.CONSENT_REMOVED_COOKIE_NAME)
    ) {
      return;
    }

    let expiryDate;

    // relative time to expire in milliseconds
    if (msToExpire) {
      expiryDate = new Date();
      expiryDate.setTime(expiryDate.getTime() + msToExpire);
    }

    if (!sameSite) {
      sameSite = "Lax";
    }

    if (sameSite === "None") {
      // SameSite None cookies must also be Secure, per spec
      isSecure = true;
    }

    if (h.isObject(value)) {
      value = JSON.stringify(value);
    }

    document.cookie =
      cookieName +
      "=" +
      encodeURIComponent(value) +
      (expiryDate ? ";expires=" + expiryDate.toUTCString() : "") +
      ";path=" +
      (path || "/") +
      (domain ? ";domain=" + domain : "") +
      (isSecure ? ";secure" : "") +
      ";SameSite=" +
      sameSite;

    // check the cookie was actually set
    if (
      (!msToExpire || msToExpire >= 0) &&
      this.getCookie(cookieName) !== String(value)
    ) {
      var msg =
        "There was an error setting cookie `" +
        cookieName +
        "`. Please check domain and path.";
      h.logConsoleError(msg);
    }
  }

  /**
   * Inits the custom variables object
   *
   * @returns {object}
   */
  getCustomVariablesFromCookie() {
    let cookie = this.getCookie("cvar");

    if (cookie && cookie.length) {
      try {
        cookie = JSON.parse(cookie);

        if (h.isObject(cookie)) {
          return cookie;
        }
      } catch (ignore) {
        //ignore
      }
    }

    return {};
  }

  /**
   * @param {string} domainToTest
   * @returns {boolean}
   */
  isPossibleToSetCookieOnDomain(domainToTest) {
    var testCookieName = this.#getCookieName("testcookie_domain");
    var valueToSet = "testvalue";
    this.setCookie(
      testCookieName,
      valueToSet,
      10000,
      null,
      domainToTest,
      this.configCookieIsSecure,
      this.configCookieSameSite,
    );

    if (this.getCookie(testCookieName) === valueToSet) {
      this.deleteCookie(testCookieName, null, domainToTest);

      return true;
    }

    return false;
  }

  /**
   * Gets all cookies with the `configCookieNamePrefix` prefix; a.k.a the ones Eave manages
   *
   * @returns {string[][]} list of eave cookie key/value pairs, ["cookieName", "cookieValue"]
   */
  getEaveCookies() {
    const eaveCookies = [];

    const urlParamifiedCookies = document.cookie.replace(
      /;[ ]*/g,
      "&",
    );
    const cookies = new URLSearchParams(urlParamifiedCookies);
    for (const [cookieName, cookieValue] of cookies) {
      if (
        cookieName.startsWith(this.configCookieNamePrefix) &&
        // ignore consent cookies; they're strictly internal operations data
        cookieName !== this.#getCookieName(this.CONSENT_REMOVED_COOKIE_NAME) &&
        cookieName !== this.#getCookieName(this.CONSENT_COOKIE_NAME) &&
        this.getCookie(cookieName) !== undefined
      ) {
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
      this.deleteCookie(
        cookieName,
        this.configCookiePath,
        this.configCookieDomain,
      );
    }

    this.configCookiesDisabled = savedConfigCookiesDisabled;
  }

  /**
   * Delete a first-party Eave cookie
   * Since we delete via `this.setCookie`, `cookieName` will automatically be prefixed
   * with `configCookieNamePrefix`.
   *
   * @param {string} cookieName
   * @param {string | null} [path]
   * @param {string} [domain]
   * @noreturn
   */
  deleteCookie(cookieName, path, domain) {
    this.setCookie(cookieName, "", -129600000, path, domain);
  }

  /**
   * Does browser have cookies enabled (for this site)?
   *
   * @returns {boolean}
   */
  hasCookies() {
    if (this.configCookiesDisabled) {
      return false;
    }

    return navigator.cookieEnabled;
  }

  /**
   * @returns {string | undefined}
   */
  getSession() {
    return this.getCookie(this.SESSION_ID_COOKIE_NAME);
  }

  /**
   * Resets the expiration of the session cookie, or sets a new
   * value if there was no existing session cookie.
   *
   * @noreturn
   */
  resetOrExtendSession() {
    const sessionId = this.getSession() || h.uuidv4();
    this.setCookie(
      this.SESSION_ID_COOKIE_NAME,
      sessionId,
      this.configSessionCookieTimeout,
      this.configCookiePath,
      this.configCookieDomain,
      this.configCookieIsSecure,
      this.configCookieSameSite,
    );
  }

  /**
   * Set visitor ID if it hasnt yet been set.
   *
   * @noreturn
   */
  setVisitorId() {
    if (!this.getCookie(this.VISITOR_ID_COOKIE_NAME)) {
      this.setCookie(this.VISITOR_ID_COOKIE_NAME, h.uuidv4());
    }
  }
}
