// @ts-check

import { consentManager } from "./consent.mjs";
import { COOKIE_NAME_PREFIX, cookieManager } from "./cookies.mjs"; // eslint-disable-line no-unused-vars
import { uuidv4 } from "../util/helpers.mjs";
import { COOKIE_CONSENT_GRANTED_EVENT_TYPE, SESSION_EXTENDED_EVENT_TYPE } from "../internal/event-types.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import * as Types from "../types.mjs"; // eslint-disable-line no-unused-vars

const SESSION_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}session_id`;
const SESSION_START_MS_COOKIE_NAME = `${COOKIE_NAME_PREFIX}session_start`;
const VISITOR_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}visitor_id`;
const REFERRER_COOKIE_NAME = `${COOKIE_NAME_PREFIX}referrer`;

const SESSION_LENGTH_SEC = 30 * 60;
const VISITOR_COOKIE_MAX_AGE_SEC = 60 * 60 * 24 * 400; // 400 days (maximum allowed value)
const REFERRER_COOKIE_MAX_AGE_SEC = 60 * 60 * 24 * 180; // 180 days (approximately 6 months)

// class SessionManager {
//   constructor() {
//     window.addEventListener(COOKIE_CONSENT_GRANTED_EVENT_TYPE, this);
//     this.#initialize();
//   }

/**
 * Interface for EventTarget.dispatchEvent()
 *
 * @param {Event} event
 *
 * @noreturn
 */
function handleEvent(event) {
  switch (event.type) {
    case COOKIE_CONSENT_GRANTED_EVENT_TYPE: {
      this.#initialize();
      break;
    }

    default: {
      break;
    }
  }
}

/**
 * @returns {string | undefined}
 */
function getSessionId() {
  return cookieManager.getCookie(SESSION_ID_COOKIE_NAME);
}

/**
 * @returns {number | undefined}
 */
function getSessionStartMs() {
  const start = cookieManager.getCookie(SESSION_START_MS_COOKIE_NAME);
  if (start === undefined) {
    return;
  }

  try {
    return parseInt(start, 10);
  } catch (e) {
    eaveLogger.error(e);
    return;
  }
}

/**
 * @returns {number | undefined}
 */
function getSessionDurationMs() {
  const start = getSessionStartMs();
  if (start === undefined) {
    return;
  }

  const now = new Date().getTime();
  return now - start;
}

/**
 * Resets the expiration of the session cookie, or sets a new
 * value if there was no existing session cookie.
 *
 * @noreturn
 */
function startOrExtendSession() {
  if (consentManager.isCookieConsentRevoked()) {
    return;
  }

  let sessionId = getSessionId();
  let sessionStart = getSessionStartMs();

  if (!sessionId) {
    sessionId = uuidv4();
  }

  if (!sessionStart) {
    sessionStart = new Date().getTime();
  }

  cookieManager.setCookie({
    name: SESSION_ID_COOKIE_NAME,
    value: sessionId,
    maxAgeSeconds: SESSION_LENGTH_SEC,
  });

  cookieManager.setCookie({
    name: SESSION_START_MS_COOKIE_NAME,
    value: sessionStart.toString(),
    maxAgeSeconds: SESSION_LENGTH_SEC,
  });
}

/**
 * Get visitor ID (from first party cookie)
 *
 * @returns {string | undefined} Visitor ID
 */
function getVisitorId() {
  return cookieManager.getCookie(VISITOR_ID_COOKIE_NAME);
};

/**
 * Get referrer (from first party cookie)
 *
 * @returns {string | undefined} Visitor ID
 */
function getReferrer() {
  return cookieManager.getCookie(REFERRER_COOKIE_NAME);
};

/**
 * set referrer
 *
 * @param {string} referrer
 *
 * @noreturn
 */
function setReferrer(referrer) {
  // window.top?.document.referrer || window.parent.document.referrer || document.referrer;
  if (consentManager.isCookieConsentRevoked()) {
    return;
  }

  cookieManager.setCookie({
    name: REFERRER_COOKIE_NAME,
    value: referrer,
    maxAgeSeconds: REFERRER_COOKIE_MAX_AGE_SEC,
  });
};

/**
 * @noreturn
 */
function initializeVisitorId() {
  if (consentManager.isCookieConsentRevoked()) {
    return;
  }

  const visitorId = getVisitorId();
  if (!visitorId) {
    cookieManager.setCookie({
      name: VISITOR_ID_COOKIE_NAME,
      value: uuidv4(),
      maxAgeSeconds: VISITOR_COOKIE_MAX_AGE_SEC,
    });
  }
}

/**
 * @noreturn
 */
function startSession() {
  initializeVisitorId();
  startOrExtendSession();
}

// }

// export const sessionManager = new SessionManager();