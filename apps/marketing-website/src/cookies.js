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

export const cookiePrefix = 'ev_';

export function saveCookie(key, value) {
  cookies.set(key, value, {
    path: '/',
    domain: window.eave.cookieDomain || '.eave.fyi',
    maxAge: 34560000,
  });
}

export function saveTrackingInfo() {
  const visitorId = cookies.get('visitor_id') || uuidv4();
  saveCookie('visitor_id', visitorId);

  const queryParams = new URLSearchParams(window.location.search);

  availableTrackingParams.forEach((paramName) => {
    const paramValue = queryParams.get(paramName);
    if (paramValue) {
      saveCookie(`${cookiePrefix}${paramName}`, paramValue);
    }
  });
}

export function getTrackingInfo() {
  return availableTrackingParams.reduce((acc, paramName) => {
    const cookieName = `${cookiePrefix}${paramName}`;
    const value = cookies.get(cookieName);
    if (value) {
      acc[cookieName] = value;
    }
    return acc;
  }, {});
}
