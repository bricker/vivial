import { consentManager } from "./managers/consent.mjs";

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