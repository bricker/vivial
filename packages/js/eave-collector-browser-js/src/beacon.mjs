
/**
 * @param {Types.RequestPayload[]} payloads
 *
 * @returns {boolean}
 */
function sendPostRequestViaSendBeacon(payloads) {
  // [bcr] supported in all major browsers
  // let isSupported = supportsSendBeacon();

  // if (!isSupported) {
  //   return false;
  // }

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

    // [bcr] we only support POST
    // if (fallbackToGet && !shouldForcePost(request)) {
    //   blob = new Blob([], headers);
    //   url = url + (url.indexOf("?") < 0 ? "?" : "&") + request;
    // }

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

  // if (success && callback) {
  //   callback({
  //     payload,
  //     trackerUrl: configTrackerUrl,
  //     success: true,
  //     // [bcr] we always use beacon
  //     // isSendBeacon: true,
  //   });
  // }

  // [bcr] check feature not currently supported
  // // If the query parameter indicating this is a test exists, close after first request is sent
  // closeWindowIfJsTrackingCodeInstallCheck();
}