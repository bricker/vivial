// @ts-check

import { uuidv4 } from "./helpers.mjs";
import { consentManager } from "./managers/consent.mjs";
import { enableClickTracking } from "./triggers/click.mjs";
import { enableFormTracking } from "./triggers/form-submit.mjs";
import { trackPageView } from "./triggers/page-view.mjs";
import * as Types from "./types.mjs"; // eslint-disable-line no-unused-vars

/** @type {string | undefined} */
// @ts-ignore - this is a known global variable implicitly set on the window.
export const clientId = EAVE_CLIENT_ID; // eslint-disable-line no-undef

/** @type {Types.GlobalEaveState} */
export const eaveState = {
  /**
   * A unique ID per page view.
   * This initially gets set every time the document loads, but it may be changed by the navigation tracking too (eg React navigation).
   */
  pageViewId: uuidv4(),
};

/** @type {Types.EaveInterface} */
const eaveInterface   = {
  enableAll() {
    consentManager.setIsCookieConsentRevoked(false);
    consentManager.setIsTrackingConsentRevoked(false);
  },

  disableAll() {
    consentManager.setIsCookieConsentRevoked(true);
    consentManager.setIsTrackingConsentRevoked(true);
  },

  enableCookies() {
    consentManager.setIsCookieConsentRevoked(false);
  },

  disableCookies() {
    consentManager.setIsCookieConsentRevoked(true);
  },

  enableTracking() {
    consentManager.setIsTrackingConsentRevoked(false);
  },

  disableTracking() {
    consentManager.setIsTrackingConsentRevoked(true);
  },
};

// @ts-ignore
window.eave = eaveInterface;

trackPageView();
enableNavigationTracking();
enableClickTracking();
enableFormTracking();
