import {
  ConsentChoice,
  setCookieConsentChoice,
  setTrackingConsentChoice,
} from "./consent";
import { initializeCookieModule } from "./cookies";
import { eaveLogger } from "./logging";
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

  setLogLevel(level) {
    eaveLogger.level = level;
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
trackPageLoad().catch((e) => eaveLogger.error(e));
