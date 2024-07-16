import { requestManager } from "./beacon.js";
import { ConsentChoice, setCookieConsentChoice, setTrackingConsentChoice } from "./consent";
import { cookiesEventHandler } from "./cookies";
import { LOG_TAG } from "./internal/constants";
import {
  CLICK_EVENT_TYPE,
  EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE,
  HASHCHANGE_EVENT_TYPE,
  POPSTATE_EVENT_TYPE,
  SUBMIT_EVENT_TYPE,
  VISIBILITY_CHANGE_EVENT_TYPE,
} from "./internal/js-events";
import { setTrafficSourceCookieIfNecessary } from "./properties/traffic-source";
import { setOrTouchUserCookies } from "./properties/user";
import { sessionEventHandler, startOrExtendSession } from "./session";
import { clickEventHandler } from "./triggers/click";
import { formSubmitEventHandler } from "./triggers/form-submission";
import {
  hashChangeEventHandler,
  popStateEventHandler,
  trackPageLoad,
  wrapNavigationStateChangeFunctions,
} from "./triggers/navigation";
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

startOrExtendSession();
setOrTouchUserCookies();
setTrafficSourceCookieIfNecessary();
wrapNavigationStateChangeFunctions();

// Register event listeners.
// The order here is important!
// The session cookie needs to be updated before anything else happens.
window.addEventListener(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, sessionEventHandler, { passive: true });
window.addEventListener(HASHCHANGE_EVENT_TYPE, sessionEventHandler, { capture: true, passive: true });
window.addEventListener(POPSTATE_EVENT_TYPE, sessionEventHandler, { capture: true, passive: true });
document.body.addEventListener(CLICK_EVENT_TYPE, sessionEventHandler, { capture: true, passive: true });
document.body.addEventListener(SUBMIT_EVENT_TYPE, sessionEventHandler, { capture: true, passive: true });

window.addEventListener(HASHCHANGE_EVENT_TYPE, hashChangeEventHandler, { capture: true, passive: true });
window.addEventListener(POPSTATE_EVENT_TYPE, popStateEventHandler, { capture: true, passive: true });
document.body.addEventListener(CLICK_EVENT_TYPE, clickEventHandler, { capture: true, passive: true });
document.body.addEventListener(SUBMIT_EVENT_TYPE, formSubmitEventHandler, { capture: true, passive: true });

window.addEventListener(EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE, cookiesEventHandler, { passive: true });

window.addEventListener(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, requestManager, { passive: true });
window.addEventListener(EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE, requestManager, { passive: true });
document.addEventListener(VISIBILITY_CHANGE_EVENT_TYPE, requestManager);

// TODO: Are these needed? Maybe for some browsers?
// document.body.addEventListener("mouseup", handleClick, { capture: true, passive: true });
// document.body.addEventListener("mousedown", handleClick, { capture: true, passive: true });
// document.body.addEventListener("contextmenu", handleClick, { capture: true, passive: true });

trackPageLoad().catch((e) => console.error(LOG_TAG, e));
