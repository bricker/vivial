import { eaveLogger } from "../logging.js";
import { UserProperties } from "../types.js";
import { uuidv4 } from "../util/uuid.js";
import { isCookieConsentRevoked } from "../consent.js";
import { COOKIE_NAME_PREFIX, MAX_ALLOWED_COOKIE_AGE_SEC, getEaveCookie, setEaveCookie } from "../cookies.js";
import { EAVE_TRIGGER_EVENT_TYPE } from "../internal/js-events.js";

const USER_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}user_id`;
const VISITOR_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}visitor_id`;

function getUserId(): string | null {
  return getEaveCookie(USER_ID_COOKIE_NAME);
}

function setUserId(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setEaveCookie({
    name: USER_ID_COOKIE_NAME,
    value,
    maxAgeSeconds: MAX_ALLOWED_COOKIE_AGE_SEC,
  });
}

function getVisitorId(): string | null {
  return getEaveCookie(VISITOR_ID_COOKIE_NAME);
}

function setVisitorId(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setEaveCookie({
    name: VISITOR_ID_COOKIE_NAME,
    value: value,
    maxAgeSeconds: MAX_ALLOWED_COOKIE_AGE_SEC,
  })
}

export function getUserProperties(): UserProperties {
  return {
    id: getUserId(),
    visitor_id: getVisitorId(),
  }
}

function setOrRefreshUserCookies() {
  const userId = getUserId();
  if (userId) {
    setUserId(userId);
  }

  const visitorId = getVisitorId() || uuidv4();
  setVisitorId(visitorId);
}

/**
 * Register event listeners. Call this only once, when the page loads.
 */
export function initializeUserModule() {
  setOrRefreshUserCookies();
}