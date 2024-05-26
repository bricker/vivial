import { eaveLogger } from "./logging.js";
import { setIsCookieConsentRevoked, setIsTrackingConsentRevoked } from "./consent.js";
import { initializeCookieModule } from "./cookies.js";
import { initializeSessionModule } from "./session.js";
import { enableClickTracking } from "./triggers/click.js";
import { enableFormTracking } from "./triggers/form-submit.js";
import { enableNavigationTracking, trackPageLoad } from "./triggers/page-view.js";
import { EaveInterface } from "./types.js";
import { initializeDiscoveryModule } from "./properties/discovery.js";
import { initializeUserModule } from "./properties/user.js";

const eaveInterface: EaveInterface = {
  enableAll() {
    setIsCookieConsentRevoked(false);
    setIsTrackingConsentRevoked(false);
  },

  disableAll() {
    setIsCookieConsentRevoked(true);
    setIsTrackingConsentRevoked(true);
  },

  enableCookies() {
    setIsCookieConsentRevoked(false);
  },

  disableCookies() {
    setIsCookieConsentRevoked(true);
  },

  enableTracking() {
    setIsTrackingConsentRevoked(false);
  },

  disableTracking() {
    setIsTrackingConsentRevoked(true);
  },

  setLogLevel(level) {
    eaveLogger.level = level;
  }
};

// @ts-ignore: Adding an unknown property onto window (globalThis)
window.eave = eaveInterface;

initializeCookieModule();
initializeSessionModule();
initializeUserModule();
initializeDiscoveryModule();

enableNavigationTracking();
enableClickTracking();
enableFormTracking();

// Track this page view. This happens once, when this script loads.
trackPageLoad().catch((e) => eaveLogger.error(e));