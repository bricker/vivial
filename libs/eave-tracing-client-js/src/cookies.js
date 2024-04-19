import "./globals.js";
import * as h from "./helpers.js";

/**
 * CookieManager class
 */
export function CookieManager() {
  /* MEMBER FIELDS */
  // TODO: make fields accessible to outside
  const SESSION_COOKIE_NAME = "eave.session",
    CONSENT_COOKIE_NAME = "eave_consent",
    COOKIE_CONSENT_COOKIE_NAME = "eave_cookie_consent",
    CONSENT_REMOVED_COOKIE_NAME = "eave_consent_removed",
    // First-party cookie name prefix
    configCookieNamePrefix = "_ev_",
    // Life of the visitor cookie (in milliseconds)
    configVisitorCookieTimeout = 33955200000, // 13 months (365 days + 28days)
    // Life of the session cookie (in milliseconds)
    configSessionCookieTimeout = 1800000, // 30 minutes
    // Life of the referral cookie (in milliseconds)
    configReferralCookieTimeout = 15768000000, // 6 months
    // Eave cookies we manage
    configCookiesToDelete = ["id", "ses", "cvar", "ref"];

  let // First-party cookie domain
    // User agent defaults to origin hostname
    configCookieDomain,
    // First-party cookie path
    // Default is user agent defined.
    configCookiePath,
    // Whether to use "Secure" cookies that only work over SSL
    configCookieIsSecure = false,
    // Set SameSite attribute for cookies
    configCookieSameSite = "Lax",
    // First-party cookies are disabled
    configCookiesDisabled = false;

  /**
   * Get cookie value
   *
   * @returns {string|number} cookie value for `cookieName` or 0 if not found
   */
  this.getCookie = function (cookieName) {
    if (configCookiesDisabled && cookieName !== CONSENT_REMOVED_COOKIE_NAME) {
      return 0;
    }

    var cookiePattern = new RegExp("(^|;)[ ]*" + cookieName + "=([^;]*)"),
      cookieMatch = cookiePattern.exec(global.eave.documentAlias.cookie);

    return cookieMatch ? global.eave.decodeWrapper(cookieMatch[2]) : 0;
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
  this.setCookie = function (
    cookieName,
    value,
    msToExpire,
    path,
    domain,
    isSecure,
    sameSite,
  ) {
    if (configCookiesDisabled && cookieName !== CONSENT_REMOVED_COOKIE_NAME) {
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

    global.eave.documentAlias.cookie =
      cookieName +
      "=" +
      global.eave.encodeWrapper(value) +
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
  this.getCustomVariablesFromCookie = function () {
    var cookieName = this.getCookieName("cvar"),
      cookie = this.getCookie(cookieName);

    if (cookie && cookie.length) {
      cookie = global.eave.windowAlias.JSON.parse(cookie);

      if (h.isObject(cookie)) {
        return cookie;
      }
    }

    return {};
  };

  /*
   * Loads the referrer attribution information
   *
   * @returns {Array}
   *  0: campaign name
   *  1: campaign keyword
   *  2: timestamp
   *  3: raw URL
   */
  this.loadReferrerAttributionCookie = function () {
    // NOTE: if the format of the cookie changes,
    // we must also update JS tests, PHP tracker, System tests,
    // and notify other tracking clients (eg. Java) of the changes
    var cookie = this.getCookie(this.getCookieName("ref"));

    if (cookie.length) {
      try {
        cookie = global.eave.windowAlias.JSON.parse(cookie);
        if (h.isObject(cookie)) {
          return cookie;
        }
      } catch (ignore) {
        // Pre 1.3, this cookie was not JSON encoded
      }
    }

    return ["", "", 0, ""];
  };

  this.isPossibleToSetCookieOnDomain = function (domainToTest) {
    var testCookieName = configCookieNamePrefix + "testcookie_domain";
    var valueToSet = "testvalue";
    this.setCookie(
      testCookieName,
      valueToSet,
      10000,
      null,
      domainToTest,
      configCookieIsSecure,
      configCookieSameSite,
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
  this.deleteCookies = function () {
    var savedConfigCookiesDisabled = configCookiesDisabled;

    // Temporarily allow cookies just to delete the existing ones
    configCookiesDisabled = false;

    var index, cookieName;

    for (index = 0; index < configCookiesToDelete.length; index++) {
      cookieName = this.getCookieName(configCookiesToDelete[index]);
      if (
        cookieName !== CONSENT_REMOVED_COOKIE_NAME &&
        cookieName !== CONSENT_COOKIE_NAME &&
        0 !== this.getCookie(cookieName)
      ) {
        this.deleteCookie(cookieName, configCookiePath, configCookieDomain);
      }
    }

    configCookiesDisabled = savedConfigCookiesDisabled;
  };

  /*
   * Get cookie name with prefix and domain hash
   */
  this.getCookieName = function (baseName) {
    return configCookieNamePrefix + baseName;
  };

  this.deleteCookie = function (cookieName, path, domain) {
    this.setCookie(cookieName, "", -129600000, path, domain);
  };

  /*
   * Does browser have cookies enabled (for this site)?
   */
  this.hasCookies = function () {
    if (configCookiesDisabled) {
      return "0";
    }

    if (
      !h.isDefined(global.eave.windowAlias.showModalDialog) &&
      h.isDefined(global.eave.navigatorAlias.cookieEnabled)
    ) {
      return global.eave.navigatorAlias.cookieEnabled ? "1" : "0";
    }

    // for IE we want to actually set the cookie to avoid trigger a warning eg in IE see #11507
    var testCookieName = configCookieNamePrefix + "testcookie";
    this.setCookie(
      testCookieName,
      "1",
      undefined,
      configCookiePath,
      configCookieDomain,
      configCookieIsSecure,
      configCookieSameSite,
    );

    var hasCookie = this.getCookie(testCookieName) === "1" ? "1" : "0";
    this.deleteCookie(testCookieName);
    return hasCookie;
  };

  this.resetOrExtendSession = function () {
    const sessionId = this.getCookie(SESSION_COOKIE_NAME) || h.uuidv4();
    this.setCookie(
      SESSION_COOKIE_NAME,
      sessionId,
      configSessionCookieTimeout,
      undefined,
      undefined,
      true, // required true for "None" sameSite
      "None", // ensure this cookie is attached to our atom event requests
    );
  };
}
