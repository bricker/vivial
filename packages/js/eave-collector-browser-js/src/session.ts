import { COOKIE_NAME_PREFIX,  getEaveCookie, setEaveCookie } from "./cookies";
import { EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, EAVE_TRIGGER_EVENT_TYPE } from "./internal/js-events";
import { isCookieConsentRevoked } from "./consent";
import { EpochTimeStampMillis, SessionProperties } from "./types";
import { uuidv4 } from "./util/uuid";
import { compactJSONStringify, safeJSONParse } from "./util/json";
import { eaveLogger } from "./logging";

const SESSION_COOKIE_NAME = `${COOKIE_NAME_PREFIX}session`;

const SESSION_LENGTH_SEC = 30 * 60;

// The purpose of splitting these getters and setters into `getXCookie` and `getXJSON`
// is to allow to avoid un-parsing and re-parsing JSON when we're just refreshing the cookie expiry.

type SessionCookie = {
  id: string;
  start_timestamp_ms: EpochTimeStampMillis;
}

function getSessionCookie(): string | null {
  return getEaveCookie(SESSION_COOKIE_NAME);
}

function getSessionJSON(): SessionCookie | null {
  const value = getSessionCookie();
  if (!value) {
    return null;
  }

  return safeJSONParse(value);
}

function setSessionCookie(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setEaveCookie({
    name: SESSION_COOKIE_NAME,
    value: value,
    maxAgeSeconds: SESSION_LENGTH_SEC,
  });
}

function setSessionJSON(value: SessionCookie) {
  const str = compactJSONStringify(value);
  setSessionCookie(str);
}

/**
 * Resets the expiration of the session cookie, or sets a new
 * value if there was no existing session cookie.
 */
function startOrExtendSession() {
  const sessionCookie = getSessionCookie();
  if (sessionCookie) {
    eaveLogger.debug("Extending session.");
    // If the session already exists, then refresh its expiry by setting it again with the same value.
    setSessionCookie(sessionCookie);
    return;
  } else {
    // Otherwise, build a new Session and set it.
    eaveLogger.debug("Starting session.");
    const session: SessionCookie = {
      id: uuidv4(),
      start_timestamp_ms: Date.now(),
    };

    setSessionJSON(session);
  }
}

/**
 * Event handler for addEventListener
 */
function handleEvent(_evt: Event) {
  startOrExtendSession();
}

export function getSessionProperties(): SessionProperties | null {
  const json = getSessionJSON();
  if (!json) {
    return null;
  }

  const now = Date.now();
  const startTimestampMs = json.start_timestamp_ms;
  const duration_ms = startTimestampMs ? (now - startTimestampMs) : null;

  return {
    id: json.id,
    start_timestamp: startTimestampMs ? startTimestampMs / 1000 : null,
    duration_ms,
  }
}

let initialized = false;

/**
 * Register event listeners. Call this only once, when the page loads.
 */
export function initializeSessionModule() {
  eaveLogger.debug("Initializing session module.");

  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    window.addEventListener(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, handleEvent, { passive: true });
    window.addEventListener(EAVE_TRIGGER_EVENT_TYPE, handleEvent, { passive: true });
  }

  startOrExtendSession();
  initialized = true;
}
