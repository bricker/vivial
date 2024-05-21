import { getCurrentUrl } from "./window.mjs";
import * as Types from "./types.mjs"; // eslint-disable-line no-unused-vars
import { cookieManager } from "./cookies.mjs";

/** @type {Types.GlobalEaveWindow} */
const eaveWindow = window;

/**
 * Returns the URL query params to send with an event,
 * with the standard parameters (plugins, resolution, url, referrer, etc.).
 * Sends the pageview and browser settings with every request in case of race conditions.
 *
 * @param {Types.RequestPayload} payload any initial query params to attach to the request
 * @param {object} [customData] additional key-value data to attach to the request
 * @param {string} [pluginMethod] name of a function that builds on request query params
 *
 * @returns {Types.RequestPayload} built up query parameters to send with the request
 */
function getRequest(customData, pluginMethod) {
  const currentUrl = getCurrentUrl();

  if (cookieManager.configCookiesDisabled) {
    cookieManager.deleteEaveCookies();
  }

  if (configDoNotTrack) {
    return {};
  }

  const fileRegex = new RegExp("^file://", "i");
  if (
    !configFileTracking &&
    (window.location.protocol === "file:" ||
      fileRegex.test(currentUrl))
  ) {
    return {};
  }

  // trigger detection of browser feature to ensure a request might not end up in the client hints queue without being processed
  detectBrowserFeatures();

  // build out the rest of the request
  const payload = buildRequest(customData);

  if (h.isFunction(configCustomRequestContentProcessing)) {
    request = configCustomRequestContentProcessing(request);
  }

  // performance tracking
  if (
    configPerformanceTrackingEnabled &&
    performanceAvailable &&
    !performanceTracked
  ) {
    request = appendAvailablePerformanceMetrics(request);
    performanceTracked = true;
  }

  // tracker plugin hook
  if (pluginMethod) {
    request += h.executePluginMethod(pluginMethod, {
      tracker: trackerInstance,
      request: request,
    });
  }

  if (configAppendToTrackingUrl.length) {
    request += "&" + configAppendToTrackingUrl;
  }

  return request;
}


/**
 * Send request
 *
 * @param {Types.RequestPayload[]} payloads
 *
 * @noreturn
 */
function sendRequest(payloads) {
  refreshConsentStatus();
  if (!configHasConsent) {
    consentRequestsQueue.push(...payloads);
    return;
  }

  if (
    configBrowserFeatureDetection &&
    !clientHintsResolved &&
    supportsClientHints()
  ) {
    clientHintsRequestQueue.push(...payloads);
    return;
  }

  hasSentTrackingRequestYet = true;

  for (const payload of payloads) {
    if (configConsentRequired && configHasConsent) {
      // send a consent=1 when explicit consent is given for the apache logs
      payload.consent = "1";
    }

    injectBrowserFeaturesAndClientHints(payload);
  }

  if (
    sendPostRequestViaSendBeacon(payloads)
  ) {
    h.setExpireDateTime(100);
    return;
  }

  if (!heartBeatSetUp) {
    setUpHeartBeat(); // setup window events too, but only once
  }
}

  /**
 * @param {Types.RequestPayload[]} payloads
 *
 * @returns {boolean}
 */
function sendPostRequestViaSendBeacon(payloads) {
  const headers = {
    type: "application/json; charset=UTF-8",
  };
  let success = false;

  const url = configTrackerUrl;

  try {
    const json = JSON.stringify({
      events: {
        browser_event: payloads,
      }
    });

    const blob = new Blob([json], headers);

    if (configDoNotTrack) {
      console.debug("[eave]", "dnt prevented analytics.");
      // Return true to indicate to the caller that the function worked as expected.
      return true;
    }

    const success = navigator.sendBeacon(url, blob);
    if (success) {
      return true;
    } else {
      console.warn("[eave]", "failed to send analytics.");
      return false;
    }
    // returns true if the user agent is able to successfully queue the data for transfer,
    // Otherwise it returns false and we need to try the regular way
  } catch (e) {
    console.error("[eave]", e);
    return false;
  }
}


/**
 * Build args to pass with event request being fired
 *
 * @param {{[key:string]: any}} customData
 *
 * @returns {Types.RequestPayload}
 */
function buildPayload(customData) {
  const eaveClientId = eaveWindow.eaveClientId;
  const clientTs = new Date().getTime() / 1000;
  const currentPageUrl = getCurrentUrl();
  const charSet = document.characterSet;
  // send charset if document charset is not utf-8. sometimes encoding
  // of urls will be the same as this and not utf-8, which will cause problems
  // do not send charset if it is utf8 since it's assumed by default in eave

  const customVariablesCopy = customVariables;

  const /** @type {Types.RequestPayload} */ payload = {
    eaveClientId,
    clientTs,
    currentPageUrl,
    charSet,
    customData,
  };

  payload.currentQueryParams = Object.fromEntries(currentPageUrl.searchParams.entries());

  // add eave cookie context data
  for (const [cookieName, cookieValue] of cookieManager.getEaveCookies()) {
    payload[cookieName] = cookieValue;
  }

  // Custom Variables, scope "page"
  function appendCustomVariablesToArgs(args, customVariables, parameterName) {
    var customVariablesStringified =
      JSON.stringify(customVariables);
    if (customVariablesStringified.length > 2) {
      args[parameterName] = encodeURIComponent(
        customVariablesStringified,
      );
    }
  }

  const sortedCustomVarPage = h.sortObjectsByKeys(customVariablesPage);
  const sortedCustomVarEvent = h.sortObjectsByKeys(customVariablesEvent);

  appendCustomVariablesToArgs(args, sortedCustomVarPage, "cvar");
  appendCustomVariablesToArgs(args, sortedCustomVarEvent, "e_cvar");

  // Custom Variables, scope "visit"
  if (customVariables) {
    appendCustomVariablesToArgs(args, customVariables, "_cvar");

    // Don't save deleted custom variables in the cookie
    for (const i of Object.keys(customVariablesCopy)) {
      if (customVariables[i][0] === "" || customVariables[i][1] === "") {
        delete customVariables[i];
      }
    }

    if (configStoreCustomVariablesInCookie) {
      cookieManager.setCookie(
        "cvar",
        JSON.stringify(customVariables),
        cookieManager.configSessionCookieTimeout,
        cookieManager.configCookiePath,
        cookieManager.configCookieDomain,
        cookieManager.configCookieIsSecure,
        cookieManager.configCookieSameSite,
      );
    }
  }

  if (configIdPageView) {
    args["pv_id"] = configIdPageView;
  }

  return args;
}