import { isCookieConsentRevoked } from "../consent";
import { COOKIE_NAME_PREFIX, getCookie, setCookie } from "../cookies";
import { ScalarMap, TrafficSourceProperties } from "../types";
import { compactJSONStringify, safeJSONParse } from "../util/json";
import { currentTimestampSeconds } from "../util/timestamp";

const TRAFFIC_SOURCE_COOKIE_NAME = `${COOKIE_NAME_PREFIX}traffic_source`;
const TRAFFIC_SOURCE_COOKIE_MAX_AGE = 60 * 60 * 24 * 180; // 180 days (approximately 6 months)

const KNOWN_TRACKING_PARAMS = new Set([
  "gclid",
  "fbclid",
  "msclkid",
  "dclid",
  "ko_click_id",
  "rtd_cid",
  "li_fat_id",
  "ttclid",
  "twclid",
  "wbraid",
  "gbraid",
  "keyword",
  "matchtype",
  "campaign",
  "campaign_id",
  "pid",
  "cid",
]);

// The purpose of splitting these getters and setters into `getXCookie` and `getXJSON`
// is to allow to avoid un-parsing and re-parsing JSON when we're just refreshing the cookie expiry.

function getTrafficSourceCookie(): string | null {
  return getCookie(TRAFFIC_SOURCE_COOKIE_NAME);
}

function setTrafficSourceCookie(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setCookie({
    name: TRAFFIC_SOURCE_COOKIE_NAME,
    value,
    maxAgeSeconds: TRAFFIC_SOURCE_COOKIE_MAX_AGE,
  });
}

export function getTrafficSourceProperties(): TrafficSourceProperties | null {
  const value = getTrafficSourceCookie();
  if (!value) {
    return null;
  }

  return safeJSONParse<TrafficSourceProperties>(value);
}

function setTrafficSourceProperties(value: TrafficSourceProperties) {
  const json = compactJSONStringify(value);
  setTrafficSourceCookie(json);
}

function getCurrentTrackingParams(): ScalarMap<string> {
  const currentPageUrl = new URL(window.location.href);
  const trackingParams: ScalarMap<string> = {};

  // Note: query parameters can be repeated, but this only returns a single value per query param.
  // This loop takes the last value.
  // It is uncommon for a UTM param to be repeated.
  // The goal is more intuitive querying server-side.
  for (const [key, value] of currentPageUrl.searchParams) {
    const k = key.toLowerCase();
    if (k.startsWith("utm_") || KNOWN_TRACKING_PARAMS.has(k)) {
      trackingParams[k] = value;
    }
  }

  return trackingParams;
}

export function setTrafficSourceCookieIfNecessary() {
  const currentTrackingParams = getCurrentTrackingParams();
  const existingCookie = getTrafficSourceCookie();

  // If there are UTM parameters in the current URL, then we'll overwrite any existing cookie with the new parameters.
  // If there are no UTM parameters, and there IS NOT an existing cookie, then we'll set the cookie with some basic info.
  // If there are no UTM parameters, and there IS an existing cookie, then leave the cookie as-is.
  if (Object.keys(currentTrackingParams).length > 0 || existingCookie === null) {
    const trafficSourceProperties: TrafficSourceProperties = {
      timestamp: currentTimestampSeconds(),
      browser_referrer: window.top?.document.referrer || window.parent.document.referrer || document.referrer || null,
      tracking_params: currentTrackingParams,
    };

    setTrafficSourceProperties(trafficSourceProperties);
  }
}
