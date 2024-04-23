import "./globals.mjs";
import * as h from "./helpers.mjs";

/**
 * CookieManager class
 */
export class CookieManager {
  constructor() {
    this.SESSION_COOKIE_NAME = "eave.session";
    this.CONSENT_COOKIE_NAME = "eave_consent";
    this.CONTEXT_COOKIE_NAME = "eave.context";
    this.COOKIE_CONSENT_COOKIE_NAME = "eave_cookie_consent";
    this.CONSENT_REMOVED_COOKIE_NAME = "eave_consent_removed";
    // First-party cookie name prefix
    this.configCookieNamePrefix = "_eave_";
    // Life of the visitor cookie (in milliseconds)
    this.configVisitorCookieTimeout = 33955200000; // 13 months (365 days + 28days)
    // Life of the session cookie (in milliseconds)
    this.configSessionCookieTimeout = 1800000; // 30 minutes
    // Life of the referral cookie (in milliseconds)
    this.configReferralCookieTimeout = 15768000000; // 6 months
    // Eave cookies we manage
    this.configCookiesToDelete = [this.SESSION_COOKIE_NAME, this.CONTEXT_COOKIE_NAME, "cvar"];
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
   * Get cookie value
   *
   * @returns {string|number} cookie value for `cookieName` or 0 if not found
   */
  getCookie(cookieName) {
    if (
      this.configCookiesDisabled &&
      cookieName !== this.CONSENT_REMOVED_COOKIE_NAME
    ) {
      return 0;
    }

    var cookiePattern = new RegExp("(^|;)[ ]*" + cookieName + "=([^;]*)"),
      cookieMatch = cookiePattern.exec(globalThis.eave.documentAlias.cookie);

    return cookieMatch ? globalThis.eave.decodeWrapper(cookieMatch[2]) : 0;
  };

  /**
   * Set cookie value
   *
   * @param {string} cookieName
   * @param {string} value
   * @param {number} msToExpire (optional)
   * @param {string} path site path to limit cookie sharing to (default "/")
   * @param {string} domain domain to limit cookie sharing to (optional)
   * @param {boolean} isSecure wither cookie is only attached to https requests (default falsey)
   * @param {string} sameSite cookie sharing restrictions (default "Lax")
   *    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie#samesitesamesite-value
   */
  setCookie(
    cookieName,
    value,
    msToExpire,
    path,
    domain,
    isSecure,
    sameSite,
  ) {
    if (
      this.configCookiesDisabled &&
      cookieName !== this.CONSENT_REMOVED_COOKIE_NAME
    ) {
      return;
    }

    var expiryDate;

    // relative time to expire in milliseconds
    if (msToExpire) {
      expiryDate = new Date();
      expiryDate.setTime(expiryDate.getTime() + msToExpire);
    }

    if (!sameSite) {
      sameSite = "Lax";
    }

    globalThis.eave.documentAlias.cookie =
      cookieName +
      "=" +
      globalThis.eave.encodeWrapper(value) +
      (msToExpire ? ";expires=" + expiryDate.toGMTString() : "") +
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
  };

  /*
   * Inits the custom variables object
   */
  getCustomVariablesFromCookie() {
    var cookieName = this.getCookieName("cvar"),
      cookie = this.getCookie(cookieName);

    if (cookie && cookie.length) {
      cookie = globalThis.eave.windowAlias.JSON.parse(cookie);

      if (h.isObject(cookie)) {
        return cookie;
      }
    }

    return {};
  };

  isPossibleToSetCookieOnDomain(domainToTest) {
    var testCookieName = this.configCookieNamePrefix + "testcookie_domain";
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
  };

  /**
   * Deletes the set of cookies `configCookiesToDelete` that we manage
   */
  deleteCookies() {
    var savedConfigCookiesDisabled = this.configCookiesDisabled;

    // Temporarily allow cookies just to delete the existing ones
    this.configCookiesDisabled = false;

    var index, cookieName;

    for (index = 0; index < this.configCookiesToDelete.length; index++) {
      cookieName = this.getCookieName(this.configCookiesToDelete[index]);
      if (
        cookieName !== this.CONSENT_REMOVED_COOKIE_NAME &&
        cookieName !== this.CONSENT_COOKIE_NAME &&
        0 !== this.getCookie(cookieName)
      ) {
        this.deleteCookie(
          cookieName,
          this.configCookiePath,
          this.configCookieDomain,
        );
      }
    }

    this.configCookiesDisabled = savedConfigCookiesDisabled;
  };

  /*
   * Get cookie name with prefix and domain hash
   */
  getCookieName(baseName) {
    return this.configCookieNamePrefix + baseName;
  };

  deleteCookie(cookieName, path, domain) {
    this.setCookie(cookieName, "", -129600000, path, domain);
  };

  /*
   * Does browser have cookies enabled (for this site)?
   */
  hasCookies() {
    if (this.configCookiesDisabled) {
      return "0";
    }

    if (
      !h.isDefined(globalThis.eave.windowAlias.showModalDialog) &&
      h.isDefined(globalThis.eave.navigatorAlias.cookieEnabled)
    ) {
      return globalThis.eave.navigatorAlias.cookieEnabled ? "1" : "0";
    }

    // for IE we want to actually set the cookie to avoid trigger a warning eg in IE see #11507
    var testCookieName = this.configCookieNamePrefix + "testcookie";
    this.setCookie(
      testCookieName,
      "1",
      undefined,
      this.configCookiePath,
      this.configCookieDomain,
      this.configCookieIsSecure,
      this.configCookieSameSite,
    );

    var hasCookie = this.getCookie(testCookieName) === "1" ? "1" : "0";
    this.deleteCookie(testCookieName);
    return hasCookie;
  };

  getSession() {
    return this.getCookie(this.SESSION_COOKIE_NAME);
  }

  resetOrExtendSession() {
    const sessionId = this.getSession() || h.uuidv4();
    this.setCookie(
      this.SESSION_COOKIE_NAME,
      sessionId,
      this.configSessionCookieTimeout,
      this.configCookiePath,
      this.configCookieDomain,
      this.configCookieIsSecure,
      this.configCookieSameSite,
    );
  };
}
