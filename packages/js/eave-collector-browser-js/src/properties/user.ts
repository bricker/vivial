import { isCookieConsentRevoked } from "../consent";
import { COOKIE_NAME_PREFIX, MAX_ALLOWED_COOKIE_AGE_SEC, getEaveCookie, setEaveCookie } from "../cookies";
import { UserProperties } from "../types";
import { uuidv4 } from "../util/uuid";

const ACCOUNT_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}account_id`;
const VISITOR_ID_COOKIE_NAME = `${COOKIE_NAME_PREFIX}visitor_id`;

function getAccountId(): string | null {
  return getEaveCookie(ACCOUNT_ID_COOKIE_NAME);
}

function setAccountId(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setEaveCookie({
    name: ACCOUNT_ID_COOKIE_NAME,
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
  });
}

export function getUserProperties(): UserProperties {
  return {
    account_id: getAccountId(),
    visitor_id: getVisitorId(),
  };
}

export function setOrTouchUserCookies() {
  const accountId = getAccountId();
  if (accountId) {
    setAccountId(accountId);
  }

  const visitorId = getVisitorId() || uuidv4();
  setVisitorId(visitorId);
}
