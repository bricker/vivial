import { EAVE_TRIGGER_EVENT_TYPE } from "../internal/js-events.js";
import { DiscoveryProperties, JSONObject, StringMap } from "../types.js";
import { uuidv4 } from "../util/uuid.js";
import { isCookieConsentRevoked } from "../consent.js";
import { COOKIE_NAME_PREFIX, MAX_ALLOWED_COOKIE_AGE_SEC, getEaveCookie, setEaveCookie } from "../cookies.js";
import { eaveLogger } from "../logging.js";
import { compactJSONStringify, safeJSONParse } from "../util/json.js";

const KNOWN_TRACKING_PARAMS = new Set([
  "campaign",
  "gclid",
  "fbclid",
]);

const DISCOVERY_PARAMS_COOKIE_NAME = `${COOKIE_NAME_PREFIX}discovery`;
const DISCOVERY_PARAMS_COOKIE_MAX_AGE = 60 * 60 * 24 * 180; // 180 days (approximately 6 months)

// The purpose of splitting these getters and setters into `getXCookie` and `getXJSON`
// is to allow to avoid un-parsing and re-parsing JSON when we're just refreshing the cookie expiry.

function getDiscoveryParamsCookie(): string | null {
  return getEaveCookie(DISCOVERY_PARAMS_COOKIE_NAME);
}

function setDiscoveryParamsCookie(value: string) {
  if (isCookieConsentRevoked()) {
    return;
  }

  setEaveCookie({
    name: DISCOVERY_PARAMS_COOKIE_NAME,
    value,
    maxAgeSeconds: DISCOVERY_PARAMS_COOKIE_MAX_AGE,
  });
}

function setDiscoveryParamsJSON(value: DiscoveryProperties) {
  const json = compactJSONStringify(value);
  setDiscoveryParamsCookie(json);
}

function buildDiscoveryParams(): DiscoveryProperties {
  const currentPageUrl = new URL(window.location.href);
  const discoveryParams: DiscoveryProperties = {
    timestamp: new Date().getTime(),
    // This is called "browser_referrer" instead of just "referrer" in case there is a query param called "referrer"
    browser_referrer: window.top?.document.referrer || window.parent.document.referrer || document.referrer,
    utm_params: {},
  }

  // Note: query parameters can be repeated, but this only returns a single value per query param.
  // This loop takes the last value.
  // It is uncommon for a UTM param to be repeated.
  // The goal is more intuitive querying server-side.
  currentPageUrl.searchParams.forEach((key, value) => {
    if (key.startsWith("utm_") || KNOWN_TRACKING_PARAMS.has(key)) {
      discoveryParams.utm_params[key] = value;
    }
  });

  return discoveryParams;
}

export function getDiscoveryProperties(): DiscoveryProperties | null {
  const value = getDiscoveryParamsCookie();
  if (!value) {
    return null;
  }

  const json = safeJSONParse<DiscoveryProperties>(value);
  if (!json) {
    return null;
  }

  // Just returning the json variable here would be okay, but I want to be explicit here for improved typechecking.
  // Maybe unnecessary.
  return {
    browser_referrer: json.browser_referrer,
    timestamp: json.timestamp,
    campaign: json.campaign,
    fbclid: json.fbclid,
    gclid: json.gclid,
    utm_params: json.utm_params,
  };
}

function setOrRefreshDiscoveryParamsCookie() {
  const discoveryParamsCookie = getDiscoveryParamsCookie();
  if (discoveryParamsCookie) {
    // Already exists; refresh it.
    setDiscoveryParamsCookie(discoveryParamsCookie);
    return;
  } else {
    const discoveryParams = buildDiscoveryParams();
    setDiscoveryParamsJSON(discoveryParams);
  }
}

/**
 * Register event listeners. Call this only once, when the page loads.
 */
export function initializeDiscoveryModule() {
  setOrRefreshDiscoveryParamsCookie();
}