/**
 * Replace setGenerationTimeMs with this more generic function
 * Use in SPA
 * @param {number} networkTimeInMs
 * @param {number} serverTimeInMs
 * @param {number} transferTimeInMs
 * @param {number} domProcessingTimeInMs
 * @param {number} domCompletionTimeInMs
 * @param {number} onloadTimeInMs
 *
 * @noreturn
 */
this.setPagePerformanceTiming = function (
  networkTimeInMs,
  serverTimeInMs,
  transferTimeInMs,
  domProcessingTimeInMs,
  domCompletionTimeInMs,
  onloadTimeInMs,
) {
  /*members pf_net, pf_srv, pf_tfr, pf_dm1, pf_dm2, pf_onl */
  let data = {
    pf_net: networkTimeInMs,
    pf_srv: serverTimeInMs,
    pf_tfr: transferTimeInMs,
    pf_dm1: domProcessingTimeInMs,
    pf_dm2: domCompletionTimeInMs,
    pf_onl: onloadTimeInMs,
  };

  try {
    data = h.filterIn(data, h.isDefined);
    data = h.onlyPositiveIntegers(data);
    customPagePerformanceTiming = h.queryStringify(data);
    if (customPagePerformanceTiming === "") {
      h.logConsoleError(
        "setPagePerformanceTiming() called without parameters. This function needs to be called with at least one performance parameter.",
      );
      return;
    }

    performanceTracked = false; // to ensure the values are sent (again)
    performanceAvailable = true; // so appendAvailablePerformanceMetrics will be called directly
    // Otherwise performanceAvailable will be set when the pageload finished, but there is no need
    // to wait for that, when the values are set manually.
  } catch (error) {
    h.logConsoleError("setPagePerformanceTiming: " + error.toString());
  }
};


/**
 * @param {string} request
 *
 * @returns {string} the modified request
 */
function appendAvailablePerformanceMetrics(request) {
  if (customPagePerformanceTiming !== "") {
    request += customPagePerformanceTiming;
    performanceTracked = true;
    return request;
  }

  if (!performance) {
    return request;
  }

  let performanceData =
    typeof performance.timing === "object" &&
    performance.timing
      ? performance.timing
      : undefined;

  if (!performanceData) {
    performanceData =
      typeof performance.getEntriesByType ===
        "function" &&
      performance.getEntriesByType("navigation")
        ? performance.getEntriesByType("navigation")[0]
        : undefined;
  }

  if (!performanceData) {
    return request;
  }

  // note: there might be negative values because of browser bugs see https://github.com/matomo-org/matomo/pull/16516 in this case we ignore the values
  let timings = "";

  if (performanceData.connectEnd && performanceData.fetchStart) {
    if (performanceData.connectEnd < performanceData.fetchStart) {
      return request;
    }

    timings +=
      "&pf_net=" +
      Math.round(performanceData.connectEnd - performanceData.fetchStart);
  }

  if (performanceData.responseStart && performanceData.requestStart) {
    if (performanceData.responseStart < performanceData.requestStart) {
      return request;
    }

    timings +=
      "&pf_srv=" +
      Math.round(
        performanceData.responseStart - performanceData.requestStart,
      );
  }

  if (performanceData.responseStart && performanceData.responseEnd) {
    if (performanceData.responseEnd < performanceData.responseStart) {
      return request;
    }

    timings +=
      "&pf_tfr=" +
      Math.round(performanceData.responseEnd - performanceData.responseStart);
  }

  if (h.isDefined(performanceData.domLoading)) {
    if (performanceData.domInteractive && performanceData.domLoading) {
      if (performanceData.domInteractive < performanceData.domLoading) {
        return request;
      }

      timings +=
        "&pf_dm1=" +
        Math.round(
          performanceData.domInteractive - performanceData.domLoading,
        );
    }
  } else {
    if (performanceData.domInteractive && performanceData.responseEnd) {
      if (performanceData.domInteractive < performanceData.responseEnd) {
        return request;
      }

      timings +=
        "&pf_dm1=" +
        Math.round(
          performanceData.domInteractive - performanceData.responseEnd,
        );
    }
  }

  if (performanceData.domComplete && performanceData.domInteractive) {
    if (performanceData.domComplete < performanceData.domInteractive) {
      return request;
    }

    timings +=
      "&pf_dm2=" +
      Math.round(
        performanceData.domComplete - performanceData.domInteractive,
      );
  }

  if (performanceData.loadEventEnd && performanceData.loadEventStart) {
    if (performanceData.loadEventEnd < performanceData.loadEventStart) {
      return request;
    }

    timings +=
      "&pf_onl=" +
      Math.round(
        performanceData.loadEventEnd - performanceData.loadEventStart,
      );
  }

  return request + timings;
}