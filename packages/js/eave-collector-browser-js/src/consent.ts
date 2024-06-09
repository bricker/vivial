import { getEaveCookie, setEaveCookie } from "./cookies";
import { LOG_TAG } from "./internal/constants";
import {
  EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE,
  EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE,
} from "./internal/js-events";

// These cookies use a different prefix so that functions like deleteAllEaveCookies() don't affect these.
const CONSENT_COOKIE_NAME_PREFIX = "_eaveconsent.";

const COOKIE_CONSENT_CHOICE_COOKIE_NAME = `${CONSENT_COOKIE_NAME_PREFIX}cookie_consent`;
const TRACKING_CONSENT_CHOICE_COOKIE_NAME = `${CONSENT_COOKIE_NAME_PREFIX}tracking_consent`;

const CONSENT_COOKIE_MAX_AGE_SEC = 60 * 60 * 24 * 400; // 400 days (maximum allowed value)

export enum ConsentChoice {
  ACCEPTED = "1",
  REJECTED = "0",
}

export function isCookieConsentRevoked(): boolean {
  const cookie = getEaveCookie(COOKIE_CONSENT_CHOICE_COOKIE_NAME);
  return cookie === ConsentChoice.REJECTED;
}

export function setCookieConsentChoice(choice: ConsentChoice) {
  setEaveCookie({
    name: COOKIE_CONSENT_CHOICE_COOKIE_NAME,
    value: choice,
    maxAgeSeconds: CONSENT_COOKIE_MAX_AGE_SEC,
  });

  if (choice === ConsentChoice.ACCEPTED) {
    console.debug(LOG_TAG, "Cookie consent granted.");
    const event = new Event(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE);
    window.dispatchEvent(event);
  } else {
    console.debug(LOG_TAG, "Cookie consent revoked.");
    const event = new Event(EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE);
    window.dispatchEvent(event);
  }
}

export function isTrackingConsentRevoked(): boolean {
  const cookie = getEaveCookie(TRACKING_CONSENT_CHOICE_COOKIE_NAME);
  return cookie === ConsentChoice.REJECTED;
}

export function setTrackingConsentChoice(choice: ConsentChoice) {
  setEaveCookie({
    name: TRACKING_CONSENT_CHOICE_COOKIE_NAME,
    value: choice,
    maxAgeSeconds: CONSENT_COOKIE_MAX_AGE_SEC,
  });

  if (choice === ConsentChoice.ACCEPTED) {
    console.debug(LOG_TAG, "Tracking consent granted.");
    const event = new Event(EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE);
    window.dispatchEvent(event);
  } else {
    console.debug(LOG_TAG, "Tracking consent revoked.");
    const event = new Event(EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE);
    window.dispatchEvent(event);
  }
}
