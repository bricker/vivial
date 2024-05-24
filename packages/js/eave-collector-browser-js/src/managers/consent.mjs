// @ts-check

import { COOKIE_NAME_PREFIX, cookieManager } from "./cookies.mjs";
import { COOKIE_CONSENT_GRANTED_EVENT_TYPE, COOKIE_CONSENT_REVOKED_EVENT_TYPE, TRACKING_CONSENT_GRANTED_EVENT_TYPE, TRACKING_CONSENT_REVOKED_EVENT_TYPE } from "../internal/event-types.mjs";
import * as Types from "../types.mjs"; // eslint-disable-line no-unused-vars

const COOKIE_CONSENT_REVOKED_COOKIE_NAME = `${COOKIE_NAME_PREFIX}cookie_consent_revoked`;
const TRACKING_CONSENT_REVOKED_COOKIE_NAME = `${COOKIE_NAME_PREFIX}tracking_consent_revoked`;

const CONSENT_REVOKED_COOKIE_MAX_AGE_SEC = 60 * 60 * 24 * 400; // 400 days (maximum allowed value)

class ConsentManager {
  /**
   * @returns {boolean}
   */
  isCookieConsentRevoked() {
    const cookie = cookieManager.getCookie(COOKIE_CONSENT_REVOKED_COOKIE_NAME);
    return cookie !== undefined;
  }

  /**
   * @param {boolean} isRevoked
   *
   * @noreturn
   */
  setIsCookieConsentRevoked(isRevoked) {
    if (isRevoked) {
      cookieManager.setCookie({
        name: COOKIE_CONSENT_REVOKED_COOKIE_NAME,
        value: "1",
        maxAgeSeconds: CONSENT_REVOKED_COOKIE_MAX_AGE_SEC,
      });

      const event = new Event(COOKIE_CONSENT_REVOKED_EVENT_TYPE);
      window.dispatchEvent(event);
    } else {
      cookieManager.deleteCookie({ name: COOKIE_CONSENT_REVOKED_COOKIE_NAME });

      const event = new Event(COOKIE_CONSENT_GRANTED_EVENT_TYPE);
      window.dispatchEvent(event);
    }
  }

  /**
   * @returns {boolean}
   */
  isTrackingConsentRevoked() {
    const cookie = cookieManager.getCookie(TRACKING_CONSENT_REVOKED_COOKIE_NAME);
    return cookie !== undefined;
  }

  /**
   * @param {boolean} isRevoked
   *
   * @noreturn
   */
  setIsTrackingConsentRevoked(isRevoked) {
    if (isRevoked) {
      cookieManager.setCookie({
        name: TRACKING_CONSENT_REVOKED_COOKIE_NAME,
        value: "1",
        maxAgeSeconds: CONSENT_REVOKED_COOKIE_MAX_AGE_SEC,
      });

      const event = new Event(TRACKING_CONSENT_REVOKED_EVENT_TYPE);
      window.dispatchEvent(event);
    } else {
      cookieManager.deleteCookie({ name: TRACKING_CONSENT_REVOKED_COOKIE_NAME });

      const event = new Event(TRACKING_CONSENT_GRANTED_EVENT_TYPE);
      window.dispatchEvent(event);
    }
  }

}

export const consentManager = new ConsentManager();