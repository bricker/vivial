import * as Types from "./types.mjs"; // eslint-disable-line no-unused-vars
import { cookieManager } from "./cookies.mjs";

/** @type {Types.GlobalEaveWindow} */
const eaveWindow = window;

const CONSENT_COOKIE_NAME = "consent";
const COOKIE_CONSENT_COOKIE_NAME = "cookie_consent";
const CONSENT_REMOVED_COOKIE_NAME = "consent_removed";

class ConsentManager {
  /** @type {boolean} */
  consentGiven;

  constructor() {
    this.refreshConsentStatus();
  }

  /**
   * Enables cookies if they were disabled previously.
   *
   * @noreturn
   */
  setCookieConsentGiven() {
    if (cookieManager.configCookiesDisabled && !configDoNotTrack) {
      cookieManager.configCookiesDisabled = false;
      if (!configBrowserFeatureDetection) {
        this.enableBrowserFeatureDetection();
      }
      if (configTrackerSiteId && hasSentTrackingRequestYet) {
        cookieManager.setVisitorId();

        // sets attribution cookie, and updates visitorId in the backend
        // because hasSentTrackingRequestYet=true we assume there might not be another tracking
        // request within this page view so we trigger one ourselves.
        // if no tracking request has been sent yet, we don't set the attribution cookie cause eave
        // sets the cookie only when there is a tracking request. It'll be set if the user sends
        // a tracking request afterwards
        const request = getRequest("ping=1", null, "ping");
        sendRequest(request, configTrackerPause);
      }
    }
  }

  /**
   * Check first-party cookies and update the <code>configHasConsent</code> value.  Ensures that any
   * change to the user opt-in/out status in another browser window will be respected.
   *
   * @noreturn
   */
  refreshConsentStatus() {
    if (cookieManager.getCookie(CONSENT_REMOVED_COOKIE_NAME)) {
      this.consentGiven = false;
    } else if (cookieManager.getCookie(CONSENT_COOKIE_NAME)) {
      this.consentGiven = true;
    }
  }

  /**
   * When called, no cookies will be set until you have called `setCookieConsentGiven()`
   * unless consent was given previously AND you called {@link rememberCookieConsentGiven()} when the user
   * gave consent.
   *
   * This may be useful when you want to implement for example a popup to ask for cookie consent.
   * Once the user has given consent, you should call {@link setCookieConsentGiven()}
   * or {@link rememberCookieConsentGiven()}.
   *
   * If you require tracking consent for example because you are tracking personal data and GDPR applies to you,
   * then have a look at `settings.push(['requireConsent'])` instead.
   *
   * If the user has already given consent in the past, you can either decide to not call `requireCookieConsent` at all
   * or call `settings.push(['setCookieConsentGiven'])` on each page view at any time after calling `requireCookieConsent`.
   *
   * When the user gives you the consent to set cookies, you can also call `settings.push(['rememberCookieConsentGiven', optionalTimeoutInHours])`
   * and for the duration while the cookie consent is remembered, any call to `requireCoookieConsent` will be automatically ignored
   * until you call `forgetCookieConsentGiven`.
   * `forgetCookieConsentGiven` needs to be called when the user removes consent for using cookies. This means if you call `rememberCookieConsentGiven` at the
   * time the user gives you consent, you do not need to ever call `settings.push(['setCookieConsentGiven'])` as the consent
   * will be detected automatically through cookies.
   *
   * @returns {boolean}
   */
  requireCookieConsent() {
    if (this.getRememberedCookieConsent()) {
      return false;
    }
    this.disableCookies();
    return true;
  }

  /**
   * If the user has given cookie consent previously and this consent was remembered, it will return the number
   * in milliseconds since 1970/01/01 which is the date when the user has given cookie consent. Please note that
   * the returned time depends on the users local time which may not always be correct.
   *
   * @returns {string | undefined}
   */
  getRememberedCookieConsent() {
    return cookieManager.getCookie(COOKIE_CONSENT_COOKIE_NAME);
  }

  /**
   * Calling this method will remove any previously given cookie consent and it disables cookies for subsequent
   * page views. You may call this method if the user removes cookie consent manually, or if you
   * want to re-ask for cookie consent after a specific time period.
   *
   * @noreturn
   */
  forgetCookieConsentGiven() {
    cookieManager.deleteCookie(
      COOKIE_CONSENT_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );
    this.disableCookies();
  }

  /**
   * Calling this method will remember that the user has given cookie consent across multiple requests by setting
   * a cookie named "_eave_cookie_consent". You can optionally define the lifetime of that cookie in hours
   * using a parameter.
   *
   * When you call this method, we imply that the user has given cookie consent for this page view, and will also
   * imply consent for all future page views unless the cookie expires or the user
   * deletes all their cookies. Remembering cookie consent means even if you call {@link disableCookies()},
   * then cookies will still be enabled and it won't disable cookies since the user has given consent for cookies.
   *
   * Please note that this feature requires you to set the `cookieDomain` and `cookiePath` correctly. Please
   * also note that when you call this method, consent will be implied for all sites that match the configured
   * cookieDomain and cookiePath. Depending on your website structure, you may need to restrict or widen the
   * scope of the cookie domain/path to ensure the consent is applied to the sites you want.
   *
   * @param {number} hoursToExpire After how many hours the cookie consent should expire. By default the consent is valid
   *                          for 30 years unless cookies are deleted by the user or the browser prior to this
   *
   * @noreturn
   */
  rememberCookieConsentGiven(hoursToExpire) {
    if (hoursToExpire) {
      // convert hours to ms
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      // 30 years ms
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }
    this.setCookieConsentGiven();
    const now = new Date().getTime();
    cookieManager.setCookie(
      cookieManager.COOKIE_CONSENT_COOKIE_NAME,
      String(now),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
  }


  /**
   * Returns whether consent is required or not.
   *
   * @returns {boolean}
   */
  isConsentRequired() {
    return configConsentRequired;
  }

  /**
   * If the user has given consent previously and this consent was remembered, it will return the number
   * in milliseconds since 1970/01/01 which is the date when the user has given consent. Please note that
   * the returned time depends on the users local time which may not always be correct.
   *
   * @returns {number | string | null}
   */
  getRememberedConsent() {
    const value = cookieManager.getCookie(cookieManager.CONSENT_COOKIE_NAME);
    if (cookieManager.getCookie(cookieManager.CONSENT_REMOVED_COOKIE_NAME)) {
      // if for some reason the consent_removed cookie is also set with the consent cookie, the
      // consent_removed cookie overrides the consent one, and we make sure to delete the consent
      // cookie.
      if (value) {
        cookieManager.deleteCookie(
          cookieManager.CONSENT_COOKIE_NAME,
          cookieManager.configCookiePath,
          cookieManager.configCookieDomain,
        );
      }
      return null;
    }

    if (!value) {
      return null;
    }
    return value;
  }

  /**
   * Detects whether the user has given consent previously.
   *
   * @returns {boolean}
   */
  hasRememberedConsent() {
    return !!this.getRememberedConsent();
  }

  /**
   * When called, no tracking request will be sent to the eave server until you have called `setConsentGiven()`
   * unless consent was given previously AND you called {@link rememberConsentGiven()} when the user gave their
   * consent.
   *
   * This may be useful when you want to implement for example a popup to ask for consent before tracking the user.
   * Once the user has given consent, you should call {@link setConsentGiven()} or {@link rememberConsentGiven()}.
   *
   * If you require consent for tracking personal data for example, you should first call
   * `settings.push(['requireConsent'])`.
   *
   * If the user has already given consent in the past, you can either decide to not call `requireConsent` at all
   * or call `settings.push(['setConsentGiven'])` on each page view at any time after calling `requireConsent`.
   *
   * When the user gives you the consent to track data, you can also call `settings.push(['rememberConsentGiven', optionalTimeoutInHours])`
   * and for the duration while the consent is remembered, any call to `requireConsent` will be automatically ignored until you call `forgetConsentGiven`.
   * `forgetConsentGiven` needs to be called when the user removes consent for tracking. This means if you call `rememberConsentGiven` at the
   * time the user gives you consent, you do not need to ever call `settings.push(['setConsentGiven'])`.
   *
   * @noreturn
   */
  requireConsent() {
    configConsentRequired = true;
    configHasConsent = this.hasRememberedConsent();
    if (!configHasConsent) {
      // we won't call this.disableCookies() since we don't want to delete any cookies just yet
      // user might call `setConsentGiven` next
      cookieManager.configCookiesDisabled = true;
    }
    // eave.addPlugin might not be defined at this point, we add the plugin directly also to make JSLint happy
    // We also want to make sure to define an unload listener for each tracker, not only one tracker.
    eaveWindow.eave.coreConsentCounter++;
    eaveWindow.eave.plugins[
      "CoreConsent" + eaveWindow.eave.coreConsentCounter
    ] = {
      unload: function () {
        if (!configHasConsent) {
          // we want to make sure to remove all previously set cookies again
          cookieManager.deleteEaveCookies();
        }
      },
    };
  }

  /**
   * Call this method once the user has given consent. This will cause all tracking requests from this
   * page view to be sent. Please note that the given consent won't be remembered across page views. If you
   * want to remember consent across page views, call {@link rememberConsentGiven()} instead.
   *
   * It will also automatically enable cookies if they were disabled previously.
   *
   * @param {boolean} [setCookieConsent=true] Internal parameter. Defines whether cookies should be enabled or not.
   * @noreturn
   */
  setConsentGiven(setCookieConsent) {
    configHasConsent = true;
    if (!configBrowserFeatureDetection) {
      this.enableBrowserFeatureDetection();
    }
    if (!configEnableCampaignParameters) {
      this.enableCampaignParameters();
    }

    cookieManager.deleteCookie(
      cookieManager.CONSENT_REMOVED_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );

    var i, requestType;
    for (i = 0; i < consentRequestsQueue.length; i++) {
      requestType = typeof consentRequestsQueue[i][0];
      if (requestType === "string") {
        sendRequest(
          consentRequestsQueue[i][0],
          configTrackerPause,
          consentRequestsQueue[i][1],
        );
      } else if (requestType === "object") {
        sendBulkRequest(consentRequestsQueue[i][0], configTrackerPause);
      }
    }
    consentRequestsQueue = [];

    // we need to enable cookies after sending the previous requests as it will make sure that we send
    // a ping request if needed. Cookies are only set once we call `getRequest`. Above only calls sendRequest
    // meaning no cookies will be created unless we called enableCookies after at least one request has been sent.
    // this will cause a ping request to be sent that sets the cookies and also updates the newly generated visitorId
    // on the server.
    // If the user calls setConsentGiven before sending any tracking request (which usually is the case) then
    // nothing will need to be done as it only enables cookies and the next tracking request will set the cookies
    // etc.
    if (!h.isDefined(setCookieConsent) || setCookieConsent) {
      this.setCookieConsentGiven();
    }
  }

  /**
   * Calling this method will remember that the user has given consent across multiple requests by setting
   * a cookie. You can optionally define the lifetime of that cookie in hours using a parameter.
   *
   * When you call this method, we imply that the user has given consent for this page view, and will also
   * imply consent for all future page views unless the cookie expires (if timeout defined) or the user
   * deletes all their cookies. This means even if you call {@link requireConsent()}, then all requests
   * will still be tracked.
   *
   * Please note that this feature requires you to set the `cookieDomain` and `cookiePath` correctly and requires
   * that you do not disable cookies. Please also note that when you call this method, consent will be implied
   * for all sites that match the configured cookieDomain and cookiePath. Depending on your website structure,
   * you may need to restrict or widen the scope of the cookie domain/path to ensure the consent is applied
   * to the sites you want.
   *
   * @param {number} hoursToExpire After how many hours the consent should expire. By default the consent is valid
   *                          for 30 years unless cookies are deleted by the user or the browser prior to this
   *
   * @noreturn
   */
  rememberConsentGiven(hoursToExpire) {
    if (hoursToExpire) {
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }
    const setCookieConsent = true;
    // we currently always enable cookies if we remember consent cause we don't store across requests whether
    // cookies should be automatically enabled or not.
    this.setConsentGiven(setCookieConsent);
    const now = new Date().getTime();
    cookieManager.setCookie(
      cookieManager.CONSENT_COOKIE_NAME,
      String(now),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
  }

  /**
   * Calling this method will remove any previously given consent and during this page view no request
   * will be sent anymore ({@link requireConsent()}) will be called automatically to ensure the removed
   * consent will be enforced. You may call this method if the user removes consent manually, or if you
   * want to re-ask for consent after a specific time period. You can optionally define the lifetime of
   * the CONSENT_REMOVED_COOKIE_NAME cookie in hours using a parameter.
   *
   * @param {number} hoursToExpire  After how many hours the CONSENT_REMOVED_COOKIE_NAME cookie should expire.
   *                                By default the consent is valid for 30 years unless cookies are deleted by the user or the browser
   *                                prior to this
   * @noreturn
   */
  forgetConsentGiven(hoursToExpire) {
    if (hoursToExpire) {
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }

    cookieManager.deleteCookie(
      cookieManager.CONSENT_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );
    cookieManager.setCookie(
      cookieManager.CONSENT_REMOVED_COOKIE_NAME,
      String(new Date().getTime()),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
    this.forgetCookieConsentGiven();
    this.requireConsent();
  }

  /**
   * Returns true if user is opted out, false if otherwise.
   *
   * @returns {boolean}
   */
  isUserOptedOut() {
    return !configHasConsent;
  };
}

export const consentManager = new ConsentManager();