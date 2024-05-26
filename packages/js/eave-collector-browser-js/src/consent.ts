import { COOKIE_NAME_PREFIX, deleteEaveCookie, getEaveCookie, setEaveCookie } from "./cookies.js";
import { EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE, EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE, EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE } from "./internal/js-events.js";

// These cookies use a different prefix so that functions like deleteAllEaveCookies() don't affect these.
const CONSENT_COOKIE_NAME_PREFIX = "eaveconsent.";

const COOKIE_CONSENT_REVOKED_COOKIE_NAME = `${CONSENT_COOKIE_NAME_PREFIX}cookie_consent_revoked`;
const TRACKING_CONSENT_REVOKED_COOKIE_NAME = `${CONSENT_COOKIE_NAME_PREFIX}tracking_consent_revoked`;

const CONSENT_REVOKED_COOKIE_MAX_AGE_SEC = 60 * 60 * 24 * 400; // 400 days (maximum allowed value)

export function isCookieConsentRevoked(): boolean {
  const cookie = getEaveCookie(COOKIE_CONSENT_REVOKED_COOKIE_NAME);
  return !!cookie;
}

export function setIsCookieConsentRevoked(isRevoked: boolean) {
  if (isRevoked) {
    setEaveCookie({
      name: COOKIE_CONSENT_REVOKED_COOKIE_NAME,
      value: "1",
      maxAgeSeconds: CONSENT_REVOKED_COOKIE_MAX_AGE_SEC,
    });

    const event = new Event(EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE);
    window.dispatchEvent(event);
  } else {
    deleteEaveCookie({ name: COOKIE_CONSENT_REVOKED_COOKIE_NAME });

    const event = new Event(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE);
    window.dispatchEvent(event);
  }
}

export function isTrackingConsentRevoked(): boolean {
  const cookie = getEaveCookie(TRACKING_CONSENT_REVOKED_COOKIE_NAME);
  return !!cookie;
}

export function setIsTrackingConsentRevoked(isRevoked: boolean) {
  if (isRevoked) {
    setEaveCookie({
      name: TRACKING_CONSENT_REVOKED_COOKIE_NAME,
      value: "1",
      maxAgeSeconds: CONSENT_REVOKED_COOKIE_MAX_AGE_SEC,
    });

    const event = new Event(EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE);
    window.dispatchEvent(event);
  } else {
    deleteEaveCookie({ name: TRACKING_CONSENT_REVOKED_COOKIE_NAME });

    const event = new Event(EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE);
    window.dispatchEvent(event);
  }
}
