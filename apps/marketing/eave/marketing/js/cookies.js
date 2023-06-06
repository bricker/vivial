import { v4 as uuidv4 } from 'uuid';
import { Cookies } from 'react-cookie';

const cookies = new Cookies();

const availableTrackingParams = [
  'gclid',
  'msclkid',
  'fbclid',
  'keyword',
  'matchtype',
  'campaign',
  'campaign_id',
  'utm_source',
  'utm_medium',
];

export const cookiePrefixUtm = 'ev_utm_';
export const EAVE_VISITOR_ID_COOKIE = 'ev_visitor_id';
export const EAVE_ONBOARDING_STATE_COOKIE = 'ev_onboarding_state';
export const EAVE_EARLY_ACCESS_REQUEST_COOKIE = 'ev_ear';
export const GOOGLE_OPTIMIZE_EXP_COOKIE = '_gaexp';

export function getCookie(key) {
  const v = cookies.get(key);
  return v;
}

export function saveSessionCookie(key, value) {
  cookies.set(key, value, {
    path: '/',
    domain: window.eave.cookieDomain || '.eave.fyi',
  });
}

export function saveCookie(key, value) {
  cookies.set(key, value, {
    path: '/',
    domain: window.eave.cookieDomain || '.eave.fyi',
    maxAge: 34560000,
  });
}

export function saveTrackingInfo() {
  let visitorId = cookies.get(EAVE_VISITOR_ID_COOKIE);
  if (!visitorId) {
    visitorId = uuidv4();
    saveCookie(EAVE_VISITOR_ID_COOKIE, visitorId);
  }

  const queryParams = new URLSearchParams(window.location.search);

  availableTrackingParams.forEach((paramName) => {
    const paramValue = queryParams.get(paramName);
    if (paramValue) {
      saveCookie(`${cookiePrefixUtm}${paramName}`, paramValue);
    }
  });
}

export function getTrackingInfo() {
  return availableTrackingParams.reduce((acc, paramName) => {
    const cookieName = `${cookiePrefixUtm}${paramName}`;
    const value = cookies.get(cookieName);
    if (value) {
      acc[cookieName] = value;
    }
    return acc;
  }, {});
}
