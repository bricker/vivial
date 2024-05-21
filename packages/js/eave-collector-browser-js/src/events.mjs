/**
 * Log the link or click with the server
 *
 * @param {string} url
 * @param {string | number} linkType
 * @param {object | undefined} customData
 * @param {HTMLElement} [sourceElement]
 * @param {Types.RequestCallback | null} [callback]
 */
function logLink(url, linkType, customData, sourceElement, callback) {
  let linkParams = [
    "link=" + encodeURIComponent(purify(url)),
    "type=" + linkType,
  ].join("&");

    const interaction = getContentInteractionToRequestIfPossible(
      "click",
      url,
      sourceElement,
  );

  if (interaction) {
    linkParams += "&" + interaction;
  }

  const request = getRequest(linkParams, customData, "link");

  sendRequest(request, configTrackerPause, callback);
}

  /**
   * Log the event
   *
   * @param {string} category
   * @param {string} action
   * @param {string} [name]
   * @param {string} [value]
   * @param {object | null} [customData]
   * @param {Types.RequestCallback | null} [callback]
   *
   * @returns {boolean | undefined}
   */
  function logEvent(category, action, name, value, customData, callback) {
    // Category and Action are required parameters
    if (!h.isNumberOrHasLength(category) || !h.isNumberOrHasLength(action)) {
      h.logConsoleError(
        "Error while logging event: Parameters `category` and `action` must not be empty or filled with whitespaces",
      );
      return false;
    }
    const request = getRequest(
      buildEventRequest(category, action, name, value),
      customData,
      "event",
    );

    sendRequest(request, configTrackerPause, callback);
  }

/**
 * @param {string} category
 * @param {string} action
 * @param {string} [name]
 * @param {string} [value]
 * @returns {string}
 */
function buildEventRequest(category, action, name, value) {
  return (
    "e_ts=" + String(new Date().getTime() / 1000) +
    "&e_c=" + encodeURIComponent(category) +
    "&e_a=" + encodeURIComponent(action) +
    (name ? "&e_n=" + encodeURIComponent(name) : "") +
    (value
      ? "&e_v=" + encodeURIComponent(value)
      : "") +
    "&ca=1"
  );
}

  /**
 * Log the page view / visit
 *
 * @param {string | object} customTitle title to add to request params, or object with `text` attribute
 * @param {object} customData key value pairs to add to request params
 * @param {Types.RequestCallback | null} [callback]
 */
function logPageView(customTitle, customData, callback) {
  cookieManager.resetOrExtendSession();

  if (!configIdPageViewSetManually) {
    configIdPageView = h.generateUniqueId();
  }

  let request = getRequest(
    "action_name=" +
      encodeURIComponent(h.titleFixup(customTitle || configTitle)),
    customData,
    "log",
  );

  // append already available performance metrics if they were not already tracked (or appended)
  if (configPerformanceTrackingEnabled && !performanceTracked) {
    request = appendAvailablePerformanceMetrics(request);
  }

  sendRequest(request, configTrackerPause, callback);
}