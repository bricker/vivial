import { ConsentChoice, setCookieConsentChoice, setTrackingConsentChoice } from "./consent";
import { initializeCookieModule } from "./cookies";
import { LOG_TAG } from "./internal/constants";
import { initializeDiscoveryModule } from "./properties/discovery";
import { initializeUserModule } from "./properties/user";
import { initializeSessionModule } from "./session";
import { enableClickTracking } from "./triggers/click";
import { enableFormTracking } from "./triggers/form-submit";
import { enableNavigationTracking, trackPageLoad } from "./triggers/page-view";
import { EaveInterface } from "./types";

const eaveInterface: EaveInterface = {
  enableAll() {
    setCookieConsentChoice(ConsentChoice.ACCEPTED);
    setTrackingConsentChoice(ConsentChoice.ACCEPTED);
  },

  disableAll() {
    setCookieConsentChoice(ConsentChoice.REJECTED);
    setTrackingConsentChoice(ConsentChoice.REJECTED);
  },

  enableCookies() {
    setCookieConsentChoice(ConsentChoice.ACCEPTED);
  },

  disableCookies() {
    setCookieConsentChoice(ConsentChoice.REJECTED);
  },

  enableTracking() {
    setTrackingConsentChoice(ConsentChoice.ACCEPTED);
  },

  disableTracking() {
    setTrackingConsentChoice(ConsentChoice.REJECTED);
  },
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
trackPageLoad().catch((e) => console.error(LOG_TAG, e));
