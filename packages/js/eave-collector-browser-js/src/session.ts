import { isCookieConsentRevoked } from "./consent";
import { COOKIE_NAME_PREFIX, SESSION_COOKIE_NAME, SESSION_LENGTH_MAX_AGE_SEC, getCookie, setCookie } from "./cookies";
import { LOG_TAG } from "./internal/constants";
import { SessionProperties } from "./types";
import { compactJSONStringify, safeJSONParse } from "./util/json";
import { currentTimestampSeconds } from "./util/timestamp";
import { uuidv4 } from "./util/uuid";

function getSessionCookie(): string | null {
  return getCookie(SESSION_COOKIE_NAME);
}

function setSessionCookie(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setCookie({
    name: SESSION_COOKIE_NAME,
    value: value,
    maxAgeSeconds: SESSION_LENGTH_MAX_AGE_SEC,
  });
}

export function getSessionProperties(): SessionProperties | null {
  const value = getSessionCookie();
  if (!value) {
    return null;
  }

  return safeJSONParse<SessionProperties>(value);
}

function setSessionProperties(value: SessionProperties) {
  const json = compactJSONStringify(value);
  setSessionCookie(json);
}

/**
 * Updates the expiry and duration of the session, or sets a new
 * value if there was no existing session cookie.
 */
export function startOrExtendSession() {
  let sessionProperties = getSessionProperties();

  if (!sessionProperties || !sessionProperties.id || !sessionProperties.start_timestamp) {
    // If the cookie doesn't already exist, or it's missing crucial information, then set the cookie with new values.
    console.debug(LOG_TAG, "Starting session.");
    sessionProperties = {
      id: uuidv4(),
      start_timestamp: currentTimestampSeconds(),
    };
  }

  setSessionProperties(sessionProperties);
}

/**
 * Event handler for addEventListener
 */
export function sessionEventHandler(_evt: Event) {
  startOrExtendSession();
}
