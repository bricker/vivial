// @ts-check

import content from "./content.mjs";
import { CookieManager } from "./cookies.mjs";
import "./globals.mjs";
import * as h from "./helpers.mjs";
import query from "./query.mjs";
import { isVisible } from "./visibility.mjs";
// eslint-disable-next-line no-unused-vars
import * as Types from "./types.js";

/** @type {Types.GlobalEaveWindow} */
// @ts-ignore
const eaveWindow = window;

/**
 * eave Tracker class
 *
 * @param {string} [trackerUrl]
 * @param {number} [siteId]
 */
export function Tracker(trackerUrl, siteId) {
  /************************************************************
   * Private members
   ************************************************************/

  var /*<DEBUG>*/
    /*
     * registered test hooks
     */
    registeredHooks = {},
    /*</DEBUG>*/

    // constants
    trackerInstance = this,
    // Current URL and Referrer URL
    locationArray = h.urlFixup(
      document.domain,
      window.location.href,
      h.getReferrer(),
    ),
    domainAlias = h.domainFixup(locationArray[0]),
    configReferrerUrl = h.safeDecodeWrapper(locationArray[2]),
    enableJSErrorTracking = false,
    defaultRequestMethod = "GET",
    // Request method (GET or POST)
    configRequestMethod = defaultRequestMethod,
    defaultRequestContentType =
      "application/x-www-form-urlencoded; charset=UTF-8",
    // Request Content-Type header value; applicable when POST request method is used for submitting tracking events
    configRequestContentType = defaultRequestContentType,
    // Tracker URL
    configTrackerUrl = trackerUrl || "",
    // This string is appended to the Tracker URL Request (eg. to send data that is not handled by the existing setters/getters)
    configAppendToTrackingUrl = "",
    // setPagePerformanceTiming sets this manually for SPAs
    customPagePerformanceTiming = "",
    // Site ID
    configTrackerSiteId = siteId || "",
    // Document title
    configTitle = "",
    // Extensions to be treated as download links
    configDownloadExtensions = [
      "7z",
      "aac",
      "apk",
      "arc",
      "arj",
      "asc",
      "asf",
      "asx",
      "avi",
      "azw3",
      "bin",
      "csv",
      "deb",
      "dmg",
      "doc",
      "docx",
      "epub",
      "exe",
      "flv",
      "gif",
      "gz",
      "gzip",
      "hqx",
      "ibooks",
      "jar",
      "jpg",
      "jpeg",
      "js",
      "md5",
      "mobi",
      "mp2",
      "mp3",
      "mp4",
      "mpg",
      "mpeg",
      "mov",
      "movie",
      "msi",
      "msp",
      "odb",
      "odf",
      "odg",
      "ods",
      "odt",
      "ogg",
      "ogv",
      "pdf",
      "phps",
      "png",
      "ppt",
      "pptx",
      "qt",
      "qtm",
      "ra",
      "ram",
      "rar",
      "rpm",
      "rtf",
      "sea",
      "sha",
      "sha256",
      "sha512",
      "sig",
      "sit",
      "tar",
      "tbz",
      "tbz2",
      "bz",
      "bz2",
      "tgz",
      "torrent",
      "txt",
      "wav",
      "wma",
      "wmv",
      "wpd",
      "xls",
      "xlsx",
      "xml",
      "xz",
      "z",
      "zip",
    ],
    // Hosts or alias(es) to not treat as outlinks
    configHostsAlias = [domainAlias],
    // HTML anchor element classes to not track
    configIgnoreClasses = [],
    // Referrer URLs that should be excluded
    configExcludedReferrers = [".paypal.com"],
    // Query parameters to be excluded
    configExcludedQueryParams = [],
    // HTML anchor element classes to treat as downloads
    configDownloadClasses = [],
    // Maximum delay to wait for web bug image to be fetched (in milliseconds)
    configTrackerPause = 500,
    // If enabled, always use sendBeacon if the browser supports it
    configAlwaysUseSendBeacon = true,
    // Recurring heart beat after initial ping (in milliseconds)
    configHeartBeatDelay,
    // alias to circumvent circular function dependency (JSLint requires this)
    heartBeatPingIfActivityAlias,
    // Disallow hash tags in URL
    configDiscardHashTag,
    // Custom data
    configCustomData,
    // the URL parameter that will store the visitorId if cross domain linking is enabled
    // ev_vid = visitor ID
    // first part of this URL parameter will be 16 char visitor Id.
    // The second part is the 10 char current timestamp and the third and last part will be a 6 characters deviceId
    // timestamp is needed to prevent reusing the visitorId when the URL is shared. The visitorId will be
    // only reused if the timestamp is less than 45 seconds old.
    // deviceId parameter is needed to prevent reusing the visitorId when the URL is shared. The visitorId
    // will be only reused if the device is still the same when opening the link.
    // VDI = visitor device identifier
    configVisitorIdUrlParameter = "ev_vid",
    configReferralQueryParamsKey = "referrer_query_params",
    configReferralTimestampKey = "referrer_timestamp",
    configReferralUrlKey = "referrer_url",
    // Is performance tracking enabled
    configPerformanceTrackingEnabled = true,
    // will be set to true automatically once the onload event has finished
    performanceAvailable = false,
    // indicates if performance metrics for the page view have been sent with a request
    performanceTracked = false,
    // Whether Custom Variables scope "visit" should be stored in a cookie during the time of the visit
    configStoreCustomVariablesInCookie = false,
    // Custom Variables read from cookie, scope "visit"
    customVariables = false,
    configCustomRequestContentProcessing,
    // Do Not Track
    configDoNotTrack,
    // Count sites which are pre-rendered
    configCountPreRendered,
    // Enable sending campaign parameters to backend.
    configEnableCampaignParameters = true,
    // Custom Variables, scope "page"
    customVariablesPage = {},
    // Custom Variables, scope "event"
    customVariablesEvent = {},
    // Custom Dimensions (can be any scope)
    customDimensions = {},
    // Custom Variables names and values are each truncated before being sent in the request or recorded in the cookie
    customVariableMaximumLength = 200,
    // // Ecommerce product view
    // ecommerceProductView = {},
    // // Ecommerce items
    // ecommerceItems = {},
    // Browser features via client-side data collection
    browserFeatures = {},
    // Browser client hints
    clientHints = {},
    clientHintsRequestQueue = [],
    clientHintsResolved = false,
    clientHintsResolving = false,
    // Keeps track of previously tracked content impressions
    trackedContentImpressions = [],
    isTrackOnlyVisibleContentEnabled = false,
    // Guard to prevent empty visits see #6415. If there is a new visitor and the first 2 (or 3 or 4)
    // tracking requests are at nearly same time (eg trackPageView and trackContentImpression) 2 or more
    // visits will be created
    timeNextTrackingRequestCanBeExecutedImmediately = -1,
    // Guard against installing the link tracker more than once per Tracker instance
    clickListenerInstalled = false,
    linkTrackingEnabled = false,
    imageClickTrackingEnabled = false,
    crossDomainTrackingEnabled = false,
    // Guard against installing route history tracker more than once per instance
    routeHistoryTrackingEnabled = false,
    // Guard against installing button click tracker more than once per instance
    buttonClickTrackingEnabled = false,
    // Guard against double installing form tracking
    formTrackingEnabled = false,
    formTrackerInstalled = false,
    // Guard against installing the activity tracker more than once per Tracker instance
    heartBeatSetUp = false,
    hadWindowFocusAtLeastOnce = false,
    timeWindowLastFocused = null,
    // Timestamp of last tracker request sent to eave
    lastTrackerRequestTime = null,
    // Internal state of the pseudo click handler
    lastButton,
    lastTarget,
    configIdPageView,
    // Boolean indicating that a page view ID has been set manually
    configIdPageViewSetManually = false,
    // we measure how many pageviews have been tracked so plugins can use it to eg detect if a
    // pageview was already tracked or not
    numTrackedPageviews = 0,
    // whether requireConsent() was called or not
    configConsentRequired = false,
    // we always have the concept of consent. by default consent is assumed unless the end user removes it,
    // or unless a eave user explicitly requires consent (via requireConsent())
    configHasConsent = null, // initialized below
    // holds all pending tracking requests that have not been tracked because we need consent
    consentRequestsQueue = [],
    // holds the actual javascript errors if enableJSErrorTracking is on, if the very same error is
    // happening multiple times, then it will be tracked only once within the same page view
    javaScriptErrors = [],
    // a unique ID for this tracker during this request
    uniqueTrackerId = eaveWindow.eave.trackerIdCounter++,
    // whether a tracking request has been sent yet during this page view
    hasSentTrackingRequestYet = false,
    configBrowserFeatureDetection = true,
    cookieManager = new CookieManager(),
    configFileTracking = false,
    eaveClientId = null;

  configTitle = document.title;

  configHasConsent = !cookieManager.getCookie(
    cookieManager.CONSENT_REMOVED_COOKIE_NAME,
  );

  /**
   * Extract pathname from URL. element.pathname is actually supported by pretty much all browsers including
   * IE6 apart from some rare very old ones
   *
   * @param {string} url
   *
   * @returns {string}
   */
  function getPathName(url) {
    const parser = document.createElement("a");
    if (url.indexOf("//") !== 0 && url.indexOf("http") !== 0) {
      if (url.indexOf("*") === 0) {
        url = url.substr(1);
      }
      if (url.indexOf(".") === 0) {
        url = url.substr(1);
      }
      url = "http://" + url;
    }

    parser.href = content.toAbsoluteUrl(url);

    if (parser.pathname) {
      return parser.pathname;
    }

    return "";
  }

  /**
   * Whether the specified referrer url matches one of the configured excluded referrers.
   *
   * @param {string} referrerUrl
   *
   * @returns {boolean}
   */
  function isReferrerExcluded(referrerUrl) {
    var i, host, path, aliasHost, aliasPath;

    if (!referrerUrl.length || !configExcludedReferrers.length) {
      return false;
    }

    host = h.getHostName(referrerUrl);
    path = getPathName(referrerUrl);

    // ignore www subdomain
    if (host.indexOf("www.") === 0) {
      host = host.substr(4);
    }

    for (i = 0; i < configExcludedReferrers.length; i++) {
      aliasHost = h.domainFixup(configExcludedReferrers[i]);
      aliasPath = getPathName(configExcludedReferrers[i]);

      // ignore www subdomain
      if (aliasHost.indexOf("www.") === 0) {
        aliasHost = aliasHost.substr(4);
      }

      if (h.isSameHost(host, aliasHost) && h.isSitePath(path, aliasPath)) {
        return true;
      }
    }

    return false;
  }

  // /**
  //  * Checks if the special query parameter was included in the current URL indicating this
  //  * is supposed to be a tracking code install test.
  //  *
  //  * @returns {boolean}
  //  */
  // function wasJsTrackingCodeInstallCheckParamProvided() {
  //   if (
  //     eaveWindow.eave.trackerInstallCheckNonce &&
  //     eaveWindow.eave.trackerInstallCheckNonce.length > 0
  //   ) {
  //     return true;
  //   }

  //   eaveWindow.eave.trackerInstallCheckNonce = h.getUrlParameter(
  //     window.location.href,
  //     "tracker_install_check",
  //   );

  //   return (
  //     eaveWindow.eave.trackerInstallCheckNonce &&
  //     eaveWindow.eave.trackerInstallCheckNonce.length > 0
  //   );
  // }

  // /**
  //  * If the query parameter was included in the current URL indicating it's an install check, close the window
  //  */
  // function closeWindowIfJsTrackingCodeInstallCheck() {
  //   // If the query parameter indicating this is a test exists
  //   if (
  //     wasJsTrackingCodeInstallCheckParamProvided() &&
  //     h.isObject(window)
  //   ) {
  //     window.close();
  //   }
  // }

  // /*
  //  * Send image request to eave server using GET.
  //  * The infamous web bug (or beacon) is a transparent, single pixel (1x1) image
  //  */
  // function getImage(request, callback) {
  //   // make sure to actually load an image so callback gets invoked
  //   request = request.replace("send_image=0", "send_image=1");

  //   let image = new Image(1, 1);
  //   image.onload = function () {
  //     if (typeof callback === "function") {
  //       callback({
  //         request: request,
  //         trackerUrl: configTrackerUrl,
  //         success: true,
  //       });
  //     }
  //   };
  //   image.onerror = function () {
  //     if (typeof callback === "function") {
  //       callback({
  //         request: request,
  //         trackerUrl: configTrackerUrl,
  //         success: false,
  //       });
  //     }
  //   };
  //   image.src =
  //     configTrackerUrl +
  //     (configTrackerUrl.indexOf("?") < 0 ? "?" : "&") +
  //     request;

  //   // If the query parameter indicating this is a test exists, close after first request is sent
  //   closeWindowIfJsTrackingCodeInstallCheck();
  // }

  /**
   * @param {string} request
   *
   * @returns {boolean}
   */
  function shouldForcePost(request) {
    if (configRequestMethod === "POST") {
      return true;
    }
    // we force long single request urls and bulk requests over post
    return (
      !!request && (request.length > 2000 || request.indexOf('{"requests"') === 0)
    );
  }

  // function supportsSendBeacon() {
  //   return (
  //     "object" === typeof navigator &&
  //     "function" === typeof navigator.sendBeacon &&
  //     "function" === typeof Blob
  //   );
  // }

  /**
   * @param {string} request
   * @param {boolean} [fallbackToGet]
   * @param {Types.RequestCallback | null} [callback]
   *
   * @returns {boolean}
   */
  function sendPostRequestViaSendBeacon(request, fallbackToGet, callback) {
    // let isSupported = supportsSendBeacon();

    // if (!isSupported) {
    //   return false;
    // }

    const headers = {
      type: "application/x-www-form-urlencoded; charset=UTF-8",
    };
    let success = false;

    let url = configTrackerUrl;

    try {
      let blob = new Blob([request], headers);

      if (fallbackToGet && !shouldForcePost(request)) {
        blob = new Blob([], headers);
        url = url + (url.indexOf("?") < 0 ? "?" : "&") + request;
      }

      success = navigator.sendBeacon(url, blob);
      // returns true if the user agent is able to successfully queue the data for transfer,
      // Otherwise it returns false and we need to try the regular way
    } catch (e) {
      return false;
    }

    if (success && callback) {
      callback({
        request: request,
        trackerUrl: configTrackerUrl,
        success: true,
        isSendBeacon: true,
      });
    }

    // // If the query parameter indicating this is a test exists, close after first request is sent
    // closeWindowIfJsTrackingCodeInstallCheck();

    return success;
  }

  /**
   * POST request to eave server using XMLHttpRequest.
   *
   * @param {string} request
   * @param {boolean} [fallbackToGet]
   * @param {Types.RequestCallback | null} [callback]
   */
  function sendXmlHttpRequest(request, fallbackToGet, callback) {
    if (!h.isDefined(fallbackToGet) || null === fallbackToGet) {
      fallbackToGet = true;
    }

    if (
      eaveWindow.eave.isPageUnloading &&
      sendPostRequestViaSendBeacon(request, fallbackToGet, callback)
    ) {
      return;
    }

    setTimeout(function () {
      // we execute it with a little delay in case the unload event occurred just after sending this request
      // this is to avoid the following behaviour: Eg on form submit a tracking request is sent via POST
      // in this method. Then a few ms later the browser wants to navigate to the new page and the unload
      // event occurs and the browser cancels the just triggered POST request. This causes or fallback
      // method to be triggered and we execute the same request again (either as fallbackGet or sendBeacon).
      // The problem is that we do not know whether the initial POST request was already fully transferred
      // to the server or not when the onreadystatechange callback is executed and we might execute the
      // same request a second time. To avoid this, we delay the actual execution of this POST request just
      // by 50ms which gives it usually enough time to detect the unload event in most cases.

      if (
        eaveWindow.eave.isPageUnloading &&
        sendPostRequestViaSendBeacon(request, fallbackToGet, callback)
      ) {
        return;
      }
      var sentViaBeacon;

      try {
        // we use the progid Microsoft.XMLHTTP because
        // IE5.5 included MSXML 2.5; the progid MSXML2.XMLHTTP
        // is pinned to MSXML2.XMLHTTP.3.0
        const xhr = window.XMLHttpRequest
          ? new window.XMLHttpRequest()
          : window.ActiveXObject
          ? new window.ActiveXObject("Microsoft.XMLHTTP")
          : null;

        xhr.open("POST", configTrackerUrl, true);

        // fallback on error
        xhr.onreadystatechange = function () {
          if (
            this.readyState === 4 &&
            !(this.status >= 200 && this.status < 300)
          ) {
            const sentViaBeacon =
              eaveWindow.eave.isPageUnloading &&
              sendPostRequestViaSendBeacon(request, fallbackToGet, callback);

            // if (!sentViaBeacon && fallbackToGet) {
            //   getImage(request, callback);
            if (callback) {
              callback({
                request: request,
                trackerUrl: configTrackerUrl,
                success: false,
                xhr: this,
              });
            }
          } else {
            if (this.readyState === 4 && callback) {
              callback({
                request: request,
                trackerUrl: configTrackerUrl,
                success: true,
                xhr: this,
              });
            }
          }
        };

        xhr.setRequestHeader("Content-Type", configRequestContentType);

        xhr.withCredentials = true;

        xhr.send(request);
      } catch (e) {
        sentViaBeacon =
          eaveWindow.eave.isPageUnloading &&
          sendPostRequestViaSendBeacon(request, fallbackToGet, callback);
        // if (!sentViaBeacon && fallbackToGet) {
        //   getImage(request, callback);
        if (callback) {
          callback({
            request: request,
            trackerUrl: configTrackerUrl,
            success: false,
          });
        }
      }

      // // If the query parameter indicating this is a test exists, close after first request is sent
      // closeWindowIfJsTrackingCodeInstallCheck();
    }, 50);
  }

  function heartBeatOnFocus() {
    hadWindowFocusAtLeastOnce = true;
    timeWindowLastFocused = new Date().getTime();
  }

  /**
   * @returns {boolean}
   */
  function hadWindowMinimalFocusToConsiderViewed() {
    // we ping on blur or unload only if user was active for more than configHeartBeatDelay seconds on
    // the page otherwise we can assume user was not really on the page and for example only switching
    // through tabs
    const now = new Date().getTime();
    return (
      !timeWindowLastFocused ||
      now - timeWindowLastFocused > configHeartBeatDelay
    );
  }

  /**
   * @noreturn
   */
  function heartBeatOnBlur() {
    if (hadWindowMinimalFocusToConsiderViewed()) {
      heartBeatPingIfActivityAlias();
    }
  }

  /**
   * @noreturn
   */
  function heartBeatOnVisible() {
    if (
      document.visibilityState === "hidden" &&
      hadWindowMinimalFocusToConsiderViewed()
    ) {
      heartBeatPingIfActivityAlias();
    } else if (document.visibilityState === "visible") {
      timeWindowLastFocused = new Date().getTime();
    }
  }

  /**
   * Setup event handlers and timeout for initial heart beat.
   *
   * @noreturn
   */
  function setUpHeartBeat() {
    if (heartBeatSetUp || !configHeartBeatDelay) {
      return;
    }

    heartBeatSetUp = true;

    window.addEventListener("focus", heartBeatOnFocus);
    window.addEventListener("blur", heartBeatOnBlur);
    window.addEventListener("visibilitychange", heartBeatOnVisible);

    // when using multiple trackers then we need to add this event for each tracker
    eaveWindow.eave.coreHeartBeatCounter++;
    eaveWindow.eave.eave?.addPlugin(
      "HeartBeat" + eaveWindow.eave.coreHeartBeatCounter,
      {
        unload: function () {
          // we can't remove the unload plugin event when disabling heart beat timer but we at least
          // check if it is still enabled... note: when enabling heart beat, then disabling, then
          // enabling then this could trigger two requests under circumstances maybe. it's edge case though

          // we only send the heartbeat if onunload the user spent at least 15seconds since last focus
          // or the configured heatbeat timer
          if (heartBeatSetUp && hadWindowMinimalFocusToConsiderViewed()) {
            heartBeatPingIfActivityAlias();
          }
        },
      },
    );
  }

  /**
   * @param {() => void} callback
   *
   * @noreturn
   */
  function makeSureThereIsAGapAfterFirstTrackingRequestToPreventMultipleVisitorCreation(
    callback,
  ) {
    const now = new Date();
    const timeNow = now.getTime();

    lastTrackerRequestTime = timeNow;

    if (
      timeNextTrackingRequestCanBeExecutedImmediately !== -1 &&
      timeNow < timeNextTrackingRequestCanBeExecutedImmediately
    ) {
      // we are in the time frame shortly after the first request. we have to delay this request a bit to make sure
      // a visitor has been created meanwhile.

      const timeToWait = timeNextTrackingRequestCanBeExecutedImmediately - timeNow;

      setTimeout(callback, timeToWait);
      h.setExpireDateTime(timeToWait + 50); // set timeout is not necessarily executed at timeToWait so delay a bit more
      timeNextTrackingRequestCanBeExecutedImmediately += 50; // delay next tracking request by further 50ms to next execute them at same time

      return;
    }

    if (timeNextTrackingRequestCanBeExecutedImmediately === -1) {
      // it is the first request, we want to execute this one directly and delay all the next one(s) within a delay.
      // All requests after this delay can be executed as usual again
      const delayInMs = 800;
      timeNextTrackingRequestCanBeExecutedImmediately = timeNow + delayInMs;
    }

    callback();
  }

  /**
   * @noreturn
   */
  function processClientHintsQueue() {
    let requestType;

    for (let i = 0; i < clientHintsRequestQueue.length; i++) {
      requestType = typeof clientHintsRequestQueue[i][0];
      if (requestType === "string") {
        sendRequest(
          clientHintsRequestQueue[i][0],
          configTrackerPause,
          clientHintsRequestQueue[i][1],
        );
      } else if (requestType === "object") {
        sendBulkRequest(clientHintsRequestQueue[i][0], configTrackerPause);
      }
    }
    clientHintsRequestQueue = [];
  }

  /**
   * Browser features (plugins, resolution, cookies)
   *
   * @returns {object}
   */
  function detectBrowserFeatures() {
    // Browser Feature is disabled return empty object
    if (!configBrowserFeatureDetection) {
      return {};
    }

    if (supportsClientHints()) {
      detectClientHints(processClientHintsQueue);
    }

    if (h.isDefined(browserFeatures.res)) {
      return browserFeatures;
    }
    var i,
      mimeType,
      pluginMap = {
        // document types
        pdf: "application/pdf",

        // media players
        qt: "video/quicktime",
        realp: "audio/x-pn-realaudio-plugin",
        wma: "application/x-mplayer2",

        // interactive multimedia
        fla: "application/x-shockwave-flash",

        // RIA
        java: "application/x-java-vm",
        ag: "application/x-silverlight",
      };

    // detect browser features except IE < 11 (IE 11 user agent is no longer MSIE)
    if (!new RegExp("MSIE").test(navigator.userAgent)) {
      // general plugin detection
      if (
        navigator.mimeTypes &&
        navigator.mimeTypes.length
      ) {
        for (const i of Object.keys(pluginMap)) {
          mimeType = navigator.mimeTypes[pluginMap[i]];
          browserFeatures[i] = mimeType && mimeType.enabledPlugin ? "1" : "0";
        }
      }

      // Safari and Opera
      // IE6/IE7 navigator.javaEnabled can't be aliased, so test directly
      // on Edge navigator.javaEnabled() always returns `true`, so ignore it
      if (
        !new RegExp("Edge[ /](\\d+[\\.\\d]+)").test(
          navigator.userAgent,
        ) &&
        typeof navigator.javaEnabled !== "undefined" &&
        h.isDefined(navigator.javaEnabled) &&
        navigator.javaEnabled()
      ) {
        browserFeatures.java = "1";
      }

      browserFeatures.cookie = navigator.cookieEnabled
        ? "1"
        : "0";
    }

    const width = screen.width;
    const height = screen.height;
    browserFeatures.res = `${width}x${height}`;
    return browserFeatures;
  }

  /**
   * @param {string | string[]} request
   * @returns {string | string[]} the modified request
   */
  function injectBrowserFeaturesAndClientHints(request) {
    let appendix = "";
    let bfAppendix = "";

    for (const i of Object.keys(browserFeatures)) {
      bfAppendix += "&" + i + "=" + browserFeatures[i];
    }

    if (clientHints) {
      appendix =
        "&uadata=" +
        encodeURIComponent(
          JSON.stringify(clientHints),
        );
    }

    if (request instanceof Array) {
      for (let i = 0; i < request.length; i++) {
        request[i] += appendix + bfAppendix;
      }
    } else {
      request += appendix + bfAppendix;
    }

    return request;
  }

  function supportsClientHints() {
    // Not widely supported - https://developer.mozilla.org/en-US/docs/Web/API/Navigator/userAgentData
    return (
      // @ts-ignore
      h.isDefined(navigator.userAgentData) &&
      h.isFunction(
        // @ts-ignore
        navigator.userAgentData.getHighEntropyValues,
      )
    );
  }

  /**
   * @param {() => void} callback
   */
  function detectClientHints(callback) {
    if (clientHintsResolved || clientHintsResolving) {
      // skip if client hints were already resolved or a previous request already triggered it
      return;
    }

    // @ts-ignore
    if (navigator.userAgentData === undefined) {
      return;
    }

    clientHintsResolving = true;

    // Initialize with low entropy values that are always available
    clientHints = {
      // @ts-ignore
      brands: navigator.userAgentData.brands,
      // @ts-ignore
      platform: navigator.userAgentData.platform,
    };

    // try to gather high entropy values
    // currently this methods simply returns the requested values through a Promise
    // In later versions it might require a user permission
    // @ts-ignore
    navigator.userAgentData
      .getHighEntropyValues([
        "brands",
        "model",
        "platform",
        "platformVersion",
        "uaFullVersion",
        "fullVersionList",
      ])
      .then(
        function (ua) {
          if (ua.fullVersionList) {
            // if fullVersionList is available, brands and uaFullVersion isn't needed
            delete ua.brands;
            delete ua.uaFullVersion;
          }

          clientHints = ua;
          clientHintsResolved = true;
          clientHintsResolving = false;
          callback();
        },
        function (_message) {
          clientHintsResolved = true;
          clientHintsResolving = false;
          callback();
        },
      );
  }

  /**
   * @returns {string} the browser ID
   */
  function generateBrowserSpecificId() {
    const browserFeatures = detectBrowserFeatures();

    return h
      .sha1(
        (navigator.userAgent || "") +
          (navigator.platform || "") +
          JSON.stringify(browserFeatures),
      )
      .slice(0, 6);
  }

  /**
   * @returns {string} the device ID
   */
  function makeCrossDomainDeviceId() {
    const timestamp = h.getCurrentTimestampInSeconds();
    const browserId = generateBrowserSpecificId();
    const deviceId = String(timestamp) + browserId;

    return deviceId;
  }

  /**
   * Is the host local? (i.e., not an outlink)
   *
   * @param {string} hostName
   * @returns {boolean}
   */
  function isSiteHostName(hostName) {
    var i, alias, offset;

    for (i = 0; i < configHostsAlias.length; i++) {
      alias = h.domainFixup(configHostsAlias[i].toLowerCase());

      if (hostName === alias) {
        return true;
      }

      if (alias.slice(0, 1) === ".") {
        if (hostName === alias.slice(1)) {
          return true;
        }

        offset = hostName.length - alias.length;

        if (offset > 0 && hostName.slice(offset) === alias) {
          return true;
        }
      }
    }

    return false;
  }

  /**
   * Whether the specified domain name and path belong to any of the alias domains (eg. set via setDomains).
   *
   * Note: this function is used to determine whether a click on a URL will be considered an "Outlink".
   *
   * @param host
   * @param path
   * @returns {boolean}
   */
  function isSiteHostPath(host, path) {
    var i, aliasHost, aliasPath;

    for (i = 0; i < configHostsAlias.length; i++) {
      aliasHost = h.domainFixup(configHostsAlias[i]);
      aliasPath = getPathName(configHostsAlias[i]);

      if (h.isSameHost(host, aliasHost) && h.isSitePath(path, aliasPath)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Removes hash tag from the URL
   * Removes ignore_referrer/ignore_referer
   * Removes configVisitorIdUrlParameter
   *
   * URLs are purified before being recorded in the cookie,
   * or before being sent as GET parameters
   *
   * @param {string} url
   * @returns {string} the purified URL
   */
  function purify(url) {
    var targetPattern, i;

    // we need to remove this parameter here, they wouldn't be removed in eave tracker otherwise eg
    // for outlinks or referrers
    url = h.removeUrlParameter(url, configVisitorIdUrlParameter);

    // remove ignore referrer parameter if present
    url = h.removeUrlParameter(url, "ignore_referrer");
    url = h.removeUrlParameter(url, "ignore_referer");

    for (i = 0; i < configExcludedQueryParams.length; i++) {
      url = h.removeUrlParameter(url, configExcludedQueryParams[i]);
    }

    if (configDiscardHashTag) {
      targetPattern = new RegExp("#.*");

      return url.replace(targetPattern, "");
    }

    return url;
  }

  /**
   * Send request
   *
   * @param {string} request
   * @param {number} delay
   * @param {Types.RequestCallback | null} [callback]
   */
  function sendRequest(request, delay, callback) {
    if (eaveClientId) {
      request += "&eaveClientId=" + eaveClientId;
    }

    refreshConsentStatus();
    if (!configHasConsent) {
      consentRequestsQueue.push([request, callback]);
      return;
    }

    if (
      configBrowserFeatureDetection &&
      !clientHintsResolved &&
      supportsClientHints()
    ) {
      clientHintsRequestQueue.push([request, callback]);
      return;
    }

    hasSentTrackingRequestYet = true;

    if (!configDoNotTrack && request) {
      if (configConsentRequired && configHasConsent) {
        // send a consent=1 when explicit consent is given for the apache logs
        request += "&consent=1";
      }

      request = injectBrowserFeaturesAndClientHints(request);

      makeSureThereIsAGapAfterFirstTrackingRequestToPreventMultipleVisitorCreation(
        function () {
          if (
            configAlwaysUseSendBeacon &&
            sendPostRequestViaSendBeacon(request, true, callback)
          ) {
            h.setExpireDateTime(100);
            return;
          }

          if (shouldForcePost(request)) {
            sendXmlHttpRequest(request, undefined, callback);
          // } else {
          //   getImage(request, callback);
          }

          h.setExpireDateTime(delay);
        },
      );
    }
    if (!heartBeatSetUp) {
      setUpHeartBeat(); // setup window events too, but only once
    }
  }

  /**
   * @param {string[]} requests
   * @returns {boolean}
   */
  function canSendBulkRequest(requests) {
    if (configDoNotTrack) {
      return false;
    }

    return requests.length > 0;
  }

  /**
   * Send requests using bulk
   *
   * @param {string[]} requests
   * @param {number} delay
   */
  function sendBulkRequest(requests, delay) {
    if (!canSendBulkRequest(requests)) {
      return;
    }

    if (
      configBrowserFeatureDetection &&
      !clientHintsResolved &&
      supportsClientHints()
    ) {
      clientHintsRequestQueue.push([requests, null]);
      return;
    }

    if (!configHasConsent) {
      consentRequestsQueue.push([requests, null]);
      return;
    }

    hasSentTrackingRequestYet = true;

    makeSureThereIsAGapAfterFirstTrackingRequestToPreventMultipleVisitorCreation(
      function () {
        const chunks = h.arrayChunk(requests, 50);

        let i = 0,
          bulk;
        for (i; i < chunks.length; i++) {
          bulk =
            '{"requests":["?' +
            injectBrowserFeaturesAndClientHints(chunks[i]).join('","?') +
            '"],"send_image":0}';
          if (
            configAlwaysUseSendBeacon &&
            sendPostRequestViaSendBeacon(bulk, false, null)
          ) {
            // makes sure to load the next page faster by not waiting as long
            // we apply this once we know send beacon works
            h.setExpireDateTime(100);
          } else {
            sendXmlHttpRequest(bulk, false, null);
          }
        }

        h.setExpireDateTime(delay);
      },
    );
  }

  // function setSiteId(siteId) {
  //   configTrackerSiteId = siteId;
  // }

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

  /**
   * Returns if the given url contains a parameter to ignore the referrer
   * e.g. ignore_referer or ignore_referrer
   *
   * @param {string} url
   * @returns {boolean}
   */
  function hasIgnoreReferrerParameter(url) {
    return (
      h.getUrlParameter(url, "ignore_referrer") === "1" ||
      h.getUrlParameter(url, "ignore_referer") === "1"
    );
  }

  /**
   * Set referrer attribution data cookies on a new session.
   * Otherwise, no action taken.
   */
  function maybeSetReferrerAttribution() {
    const now = new Date(),
      nowTs = Math.round(now.getTime() / 1000),
      referralUrlMaxLength = 1024,
      cookieSessionValue = cookieManager.getSession(),
      currentUrl = getCurrentUrl();

    let referralUrl = getAttributionReferrerUrl();
    let referralQueryParams = getAttributionReferrerQueryParams();
    const previousReferralUrl = referralUrl;

    if (!hasIgnoreReferrerParameter(currentUrl) && !cookieSessionValue) {
      // session cookie was not found: we consider this the start of a 'session'

      if (
        h.isObjectEmpty(referralQueryParams) &&
        configEnableCampaignParameters
      ) {
        // extract and save all current qp
        const urlSearchParams = new URLSearchParams(
          window.location.search,
        );
        referralQueryParams = Object.fromEntries(urlSearchParams.entries());
      }

      // Store the referrer URL and time in the cookie;
      // referral URL depends on the first or last referrer attribution
      const currentReferrerHostName = h.getHostName(configReferrerUrl);
      const originalReferrerHostName = previousReferralUrl.length
        ? h.getHostName(previousReferralUrl)
        : "";

      if (
        currentReferrerHostName.length && // there is a referrer
        !isSiteHostName(currentReferrerHostName) && // domain is not the current domain
        !isReferrerExcluded(configReferrerUrl) && // referrer is excluded
        (!originalReferrerHostName.length || // previously empty
          isSiteHostName(originalReferrerHostName) || // previously set but in current domain
          isReferrerExcluded(referralUrl)) // previously set but excluded
      ) {
        referralUrl = configReferrerUrl;
      }

      // Set the referral cookie if we have a Referrer URL or query params on initial URL
      if (referralUrl.length) {
        cookieManager.setCookie(
          configReferralUrlKey,
          purify(referralUrl.slice(0, referralUrlMaxLength)),
        );
        cookieManager.setCookie(configReferralTimestampKey, String(nowTs));
      }
      if (!h.isObjectEmpty(referralQueryParams)) {
        cookieManager.setCookie(
          configReferralQueryParamsKey,
          referralQueryParams,
        );
        cookieManager.setCookie(configReferralTimestampKey, String(nowTs));
      }
    }
  }

  /**
   * Build args to pass with event request being fired
   *
   * @param {object} customData
   * @returns {object}
   */
  function buildRequest(customData) {
    const now = new Date();
    const currentUrl = getCurrentUrl();
    const hasIgnoreReferrerParam = hasIgnoreReferrerParameter(currentUrl);
    // send charset if document charset is not utf-8. sometimes encoding
    // of urls will be the same as this and not utf-8, which will cause problems
    // do not send charset if it is utf8 since it's assumed by default in eave

    /** @type {string | null} */
    let charSet =
      document.characterSet ||
      document.charset;
    if (!charSet || charSet.toLowerCase() === "utf-8") {
      charSet = null;
    }
    let i;
    const customVariablesCopy = customVariables;

    const args = {
      idsite: configTrackerSiteId,
      h: now.getHours(),
      m: now.getMinutes(),
      s: now.getSeconds(),
      url: encodeURIComponent(purify(currentUrl)),
    };

    // add current query params
    if (!hasIgnoreReferrerParam) {
      const urlSearchParams = new URLSearchParams(
        window.location.search,
      );
      const params = Object.fromEntries(urlSearchParams.entries());
      args.queryParams = JSON.stringify(params);
    }

    if (charSet) {
      args["cs"] = encodeURIComponent(charSet);
    }

    // add eave cookie context data
    for (const [cookieName, cookieValue] of cookieManager.getEaveCookies()) {
      args[cookieName] = cookieValue;
    }

    const customDimensionIdsAlreadyHandled = [];
    if (customData) {
      for (i in customData) {
        if (
          Object.prototype.hasOwnProperty.call(customData, i) &&
          /^dimension\d+$/.test(i)
        ) {
          const index = i.replace("dimension", "");
          customDimensionIdsAlreadyHandled.push(parseInt(index, 10));
          customDimensionIdsAlreadyHandled.push(String(index));
          args[i] = encodeURIComponent(customData[i]);
          delete customData[i];
        }
      }
    }

    if (customData && h.isObjectEmpty(customData)) {
      customData = null;
      // we deleted all keys from custom data
    }

    // // product page view
    // for (i in ecommerceProductView) {
    //   if (Object.prototype.hasOwnProperty.call(ecommerceProductView, i)) {
    //     args[i] = encodeURIComponent(ecommerceProductView[i]);
    //   }
    // }

    // custom dimensions
    for (i in customDimensions) {
      if (Object.prototype.hasOwnProperty.call(customDimensions, i)) {
        const isNotSetYet =
          -1 === h.indexOfArray(customDimensionIdsAlreadyHandled, i);
        if (isNotSetYet) {
          args["dimension" + i] = encodeURIComponent(
            customDimensions[i],
          );
        }
      }
    }

    // custom data
    if (customData) {
      args["data"] = encodeURIComponent(
        JSON.stringify(customData),
      );
    } else if (configCustomData) {
      args["data"] = encodeURIComponent(
        JSON.stringify(configCustomData),
      );
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

    // if (wasJsTrackingCodeInstallCheckParamProvided()) {
    //   args["tracker_install_check"] = eaveWindow.eave.tracker.InstallCheckNonce;
    // }

    return args;
  }

  /**
   * Returns the URL query params to send with an event,
   * with the standard parameters (plugins, resolution, url, referrer, etc.).
   * Sends the pageview and browser settings with every request in case of race conditions.
   *
   * @param {string} request any initial query params to attach to the request
   * @param {object} [customData] additional key-value data to attach to the request
   * @param {string} [pluginMethod] name of a function that builds on request query params
   *
   * @returns {string} built up query parameters to send with the request
   */
  function getRequest(request, customData, pluginMethod) {
    const currentUrl = getCurrentUrl();

    if (cookieManager.configCookiesDisabled) {
      cookieManager.deleteEaveCookies();
    }

    if (configDoNotTrack) {
      return "";
    }

    const fileRegex = new RegExp("^file://", "i");
    if (
      !configFileTracking &&
      (window.location.protocol === "file:" ||
        fileRegex.test(currentUrl))
    ) {
      return "";
    }

    // trigger detection of browser feature to ensure a request might not end up in the client hints queue without being processed
    detectBrowserFeatures();

    // build out the rest of the request
    request += h.argsToQueryParameters(buildRequest(customData));

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
   * If there was user activity since the last check, and it's been configHeartBeatDelay seconds
   * since the last tracker, send a ping request (the heartbeat timeout will be reset by sendRequest).
   *
   * @returns {boolean} whether the heartbeat was sent
   */
  heartBeatPingIfActivityAlias = function heartBeatPingIfActivity() {
    const now = new Date().getTime();

    if (!lastTrackerRequestTime) {
      return false; // no tracking request was ever sent so lets not send heartbeat now
    }

    if (lastTrackerRequestTime + configHeartBeatDelay <= now) {
      trackerInstance.ping();

      return true;
    }

    return false;
  };

  // function logEcommerce(
  //   orderId,
  //   grandTotal,
  //   subTotal,
  //   tax,
  //   shipping,
  //   discount,
  // ) {
  //   let request = "idgoal=0",
  //     items = [],
  //     sku,
  //     isEcommerceOrder = String(orderId).length;

  //   if (isEcommerceOrder) {
  //     request += "&ec_id=" + encodeURIComponent(orderId);
  //   }

  //   request += "&revenue=" + grandTotal;

  //   if (String(subTotal).length) {
  //     request += "&ec_st=" + subTotal;
  //   }

  //   if (String(tax).length) {
  //     request += "&ec_tx=" + tax;
  //   }

  //   if (String(shipping).length) {
  //     request += "&ec_sh=" + shipping;
  //   }

  //   if (String(discount).length) {
  //     request += "&ec_dt=" + discount;
  //   }

  //   if (ecommerceItems) {
  //     // Removing the SKU index in the array before JSON encoding
  //     for (sku in ecommerceItems) {
  //       if (Object.prototype.hasOwnProperty.call(ecommerceItems, sku)) {
  //         // Ensure name and category default to healthy value
  //         if (!h.isDefined(ecommerceItems[sku][1])) {
  //           ecommerceItems[sku][1] = "";
  //         }

  //         if (!h.isDefined(ecommerceItems[sku][2])) {
  //           ecommerceItems[sku][2] = "";
  //         }

  //         // Set price to zero
  //         if (
  //           !h.isDefined(ecommerceItems[sku][3]) ||
  //           String(ecommerceItems[sku][3]).length === 0
  //         ) {
  //           ecommerceItems[sku][3] = 0;
  //         }

  //         // Set quantity to 1
  //         if (
  //           !h.isDefined(ecommerceItems[sku][4]) ||
  //           String(ecommerceItems[sku][4]).length === 0
  //         ) {
  //           ecommerceItems[sku][4] = 1;
  //         }

  //         items.push(ecommerceItems[sku]);
  //       }
  //     }
  //     request +=
  //       "&ec_items=" +
  //       encodeURIComponent(
  //         JSON.stringify(items),
  //       );
  //   }
  //   request = getRequest(request, configCustomData, "ecommerce");
  //   sendRequest(request, configTrackerPause);

  //   if (isEcommerceOrder) {
  //     ecommerceItems = {};
  //   }
  // }

  // function logEcommerceOrder(
  //   orderId,
  //   grandTotal,
  //   subTotal,
  //   tax,
  //   shipping,
  //   discount,
  // ) {
  //   if (String(orderId).length && h.isDefined(grandTotal)) {
  //     logEcommerce(orderId, grandTotal, subTotal, tax, shipping, discount);
  //   }
  // }

  // function logEcommerceCartUpdate(grandTotal) {
  //   if (h.isDefined(grandTotal)) {
  //     logEcommerce("", grandTotal, "", "", "", "");
  //   }
  // }

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

  /**
   * Construct regular expression of classes
   *
   * @param {string[]} configClasses
   * @param {string} defaultClass
   * @returns {RegExp}
   */
  function getClassesRegExp(configClasses, defaultClass) {
    var i,
      classesRegExp = "(^| )(eave[_-]" + defaultClass;

    if (configClasses) {
      for (i = 0; i < configClasses.length; i++) {
        classesRegExp += "|" + configClasses[i];
      }
    }

    classesRegExp += ")( |$)";

    return new RegExp(classesRegExp);
  }

  /**
   * @param {string} url
   * @returns {boolean}
   */
  function startsUrlWithTrackerUrl(url) {
    return (
      !!configTrackerUrl && !!url && 0 === String(url).indexOf(configTrackerUrl)
    );
  }

  /**
   * Determines what type of link an anchor element is from various attributes.
   *
   * @param {string} className
   * @param {string} href
   * @param {boolean} isInLink
   * @param {boolean} hasDownloadAttribute
   *
   * @returns {number | string}
   */
  function getLinkType(className, href, isInLink, hasDownloadAttribute) {
    if (isInLink) {
      return "internal";
    }

    // does class indicate whether it is an (explicit/forced) outlink or a download?
    const downloadPattern = getClassesRegExp(configDownloadClasses, "download");

    // does file extension indicate that it is a download?
    const downloadExtensionsPattern = new RegExp(
      "\\.(" + configDownloadExtensions.join("|") + ")([?&#]|$)",
      "i",
    );

    if (
      hasDownloadAttribute ||
      downloadPattern.test(className) ||
      downloadExtensionsPattern.test(href)
    ) {
      return "download";
    }

    // browsers, such as Safari, don't downcase hostname and href
    const scriptProtocol = new RegExp(
      "^(javascript|vbscript|jscript|mocha|livescript|ecmascript):",
      "i",
    );
    if (scriptProtocol.test(href)) {
      return "script";
    }

    const mailProtocol = new RegExp("^mailto:", "i");
    if (mailProtocol.test(href)) {
      return "email";
    }

    const telephoneProtocol = new RegExp("^tel:", "i");
    if (telephoneProtocol.test(href)) {
      return "telephone";
    }

    return "external";
  }

  /**
   * Traverse up DOM from `target` to find node passing `isTargetNode` check
   *
   * @param {(string) => boolean} isTargetNode check for matching html element nodeName
   * @param {Node} target DOM node to traverse from
   * @return {Node | undefined} the matching DOM node, if any
   */
  function getTargetNode(isTargetNode, target) {
    const ignorePattern = getClassesRegExp(configIgnoreClasses, "ignore");
    while (target && target.parentNode && !isTargetNode(target.nodeName)) {
      target = target.parentNode;
    }

    if (
      target &&
      isTargetNode(target.nodeName) &&
      // @ts-ignore
      !ignorePattern.test(target.className)
    ) {
      return target;
    }
    return undefined;
  }

  /**
   * Get anchor tag data if the link click is not to be ignored.
   *
   * @param {HTMLElement} sourceElement
   *
   * @returns {{type: string | number, href: string} | undefined}
   */
  function getLinkIfShouldBeProcessed(sourceElement) {
    // @ts-ignore - force-cast to HTMLLinkElement
    const /** @type {HTMLLinkElement | undefined} */ _sourceElement = getTargetNode(isLinkNode, sourceElement);

    if (!_sourceElement) {
      return;
    }

    if (!query.hasNodeAttribute(_sourceElement, "href")) {
      return;
    }

    if (!h.isDefined(_sourceElement.href)) {
      return;
    }

    const url = new URL(_sourceElement.href);
    const originalSourcePath = url.pathname || getPathName(_sourceElement.href);

    // browsers, such as Safari, don't downcase hostname and href
    const originalSourceHostName = url.hostname || h.getHostName(_sourceElement.href);
    const sourceHostName = originalSourceHostName.toLowerCase();
    const sourceHref = _sourceElement.href.replace(
      originalSourceHostName,
      sourceHostName,
    );

    // browsers, such as Safari, don't downcase hostname and href
    const scriptProtocol = new RegExp(
      "^(javascript|vbscript|jscript|mocha|livescript|ecmascript|mailto|tel):",
      "i",
    );

    if (!scriptProtocol.test(sourceHref)) {
      if (!_sourceElement.className) {
        return;
      }
      // track outlinks and all downloads
      const linkType = getLinkType(
        _sourceElement.className,
        sourceHref,
        isSiteHostPath(sourceHostName, originalSourcePath),
        query.hasNodeAttribute(_sourceElement, "download"),
      );

      if (linkType) {
        return {
          type: linkType,
          href: sourceHref,
        };
      }
    }

    // track all link types (including internal)
    const linkType = getLinkType(
      sourceElement.className,
      sourceHref,
      isSiteHostPath(sourceHostName, originalSourcePath),
      query.hasNodeAttribute(sourceElement, "download"),
    );

    return {
      type: linkType,
      href: sourceHref,
    };
  }

  /**
   * @param {any} interaction
   * @param {string} name
   * @param {any} piece
   * @param {any} target
   *
   * @returns {string | undefined}
   */
  function buildContentInteractionRequest(interaction, name, piece, target) {
    const params = content.buildInteractionRequestParams(
      interaction,
      name,
      piece,
      target,
    );

    if (!params) {
      return;
    }

    return getRequest(params, null, "contentInteraction");
  }

  /**
   * @param {Node} contentNode
   * @param {Node} interactedNode
   *
   * @returns {boolean}
   */
  function isNodeAuthorizedToTriggerInteraction(contentNode, interactedNode) {
    if (!contentNode || !interactedNode) {
      return false;
    }

    let targetNode = content.findTargetNode(contentNode);

    if (content.shouldIgnoreInteraction(targetNode)) {
      // interaction should be ignored
      return false;
    }

    targetNode = content.findTargetNodeNoDefault(contentNode);
    if (targetNode && !h.containsNodeElement(targetNode, interactedNode)) {
      /**
       * There is a target node defined but the clicked element is not within the target node. example:
       * <div data-track-content><a href="Y" data-content-target>Y</a><img src=""/><a href="Z">Z</a></div>
       *
       * The user clicked in this case on link Z and not on target Y
       */
      return false;
    }

    return true;
  }

  /**
   * @param {string} interaction
   * @param {string} fallbackTarget
   * @param {Node} [anyNode]
   *
   * @returns {string | undefined}
   */
  function getContentInteractionToRequestIfPossible(
    interaction,
    fallbackTarget,
    anyNode,
  ) {
    if (!anyNode) {
      return;
    }

    const contentNode = content.findParentContentNode(anyNode);

    if (!contentNode) {
      // we are not within a content block
      return;
    }

    if (!isNodeAuthorizedToTriggerInteraction(contentNode, anyNode)) {
      return;
    }

    const contentBlock = content.buildContentBlock(contentNode);

    if (!contentBlock) {
      return;
    }

    if (!contentBlock.target && fallbackTarget) {
      contentBlock.target = fallbackTarget;
    }

    return content.buildInteractionRequestParams(
      interaction,
      contentBlock.name,
      contentBlock.piece,
      contentBlock.target,
    );
  }

  /**
   * @param {any} contentBlock
   * @returns {boolean}
   */
  function wasContentImpressionAlreadyTracked(contentBlock) {
    if (!trackedContentImpressions || !trackedContentImpressions.length) {
      return false;
    }

    var index, trackedContent;

    for (index = 0; index < trackedContentImpressions.length; index++) {
      trackedContent = trackedContentImpressions[index];

      if (
        trackedContent &&
        trackedContent.name === contentBlock.name &&
        trackedContent.piece === contentBlock.piece &&
        trackedContent.target === contentBlock.target
      ) {
        return true;
      }
    }

    return false;
  }

  /**
   * @param {Node} targetNode
   * @returns {(event: Event) => string | number | false | null | undefined}
   */
  function trackContentImpressionClickInteraction(targetNode) {
    return function (event) {
      if (!targetNode) {
        return;
      }

      const contentBlock = content.findParentContentNode(targetNode);

      if (!contentBlock) {
        return false;
      }

      let interactedElement;
      if (event) {
        interactedElement = event.target;
      }
      if (!interactedElement) {
        interactedElement = targetNode;
      }

      if (
        !isNodeAuthorizedToTriggerInteraction(contentBlock, interactedElement)
      ) {
        return;
      }

      const theTargetNode = content.findTargetNode(contentBlock);

      if (!theTargetNode || content.shouldIgnoreInteraction(theTargetNode)) {
        return false;
      }

      const link = getLinkIfShouldBeProcessed(theTargetNode);

      if (linkTrackingEnabled && link && link.type) {
        return link.type; // will be handled via outlink or download.
      }

      return trackerInstance.trackContentInteractionNode(
        interactedElement,
        "click",
      );
    };
  }

  /**
   * @param {Element[]} contentNodes
   */
  function setupInteractionsTracking(contentNodes) {
    if (!contentNodes || !contentNodes.length) {
      return;
    }

    var index, targetNode;
    for (index = 0; index < contentNodes.length; index++) {
      targetNode = content.findTargetNode(contentNodes[index]);

      if (targetNode && !targetNode.contentInteractionTrackingSetupDone) {
        targetNode.contentInteractionTrackingSetupDone = true;

        targetNode.addEventListener(
          "click",
          trackContentImpressionClickInteraction(targetNode),
        );
      }
    }
  }

  /**
   * Log all content pieces
   *
   * @param {any} contents
   * @param {Element[]} contentNodes
   * @returns {string[]}
   */
  function buildContentImpressionsRequests(contents, contentNodes) {
    if (!contents || !contents.length) {
      return [];
    }

    let index;
    let request;

    for (index = 0; index < contents.length; index++) {
      if (wasContentImpressionAlreadyTracked(contents[index])) {
        contents.splice(index, 1);
        index--;
      } else {
        trackedContentImpressions.push(contents[index]);
      }
    }

    if (!contents || !contents.length) {
      return [];
    }

    setupInteractionsTracking(contentNodes);

    const requests = [];

    for (index = 0; index < contents.length; index++) {
      request = getRequest(
        content.buildImpressionRequestParams(
          contents[index].name,
          contents[index].piece,
          contents[index].target,
        ),
        undefined,
        "contentImpressions",
      );

      if (request) {
        requests.push(request);
      }
    }

    return requests;
  }

  /**
   * Log all content pieces
   *
   * @param {Element[]} contentNodes
   * @returns {string[]}
   */
  function getContentImpressionsRequestsFromNodes(contentNodes) {
    const contents = content.collectContent(contentNodes);

    return buildContentImpressionsRequests(contents, contentNodes);
  }

  /**
   * Log currently visible content pieces
   *
   * @param {HTMLElement[]} contentNodes
   * @returns {string[]}
   */
  function getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
    contentNodes,
  ) {
    if (!contentNodes || !contentNodes.length) {
      return [];
    }

    let index;

    for (index = 0; index < contentNodes.length; index++) {
      if (!content.isNodeVisible(contentNodes[index])) {
        contentNodes.splice(index, 1);
        index--;
      }
    }

    if (!contentNodes || !contentNodes.length) {
      return [];
    }

    return getContentImpressionsRequestsFromNodes(contentNodes);
  }

  /**
   * @param {string} contentName
   * @param {any} contentPiece
   * @param {any} contentTarget
   * @returns {string}
   */
  function buildContentImpressionRequest(
    contentName,
    contentPiece,
    contentTarget,
  ) {
    const params = content.buildImpressionRequestParams(
      contentName,
      contentPiece,
      contentTarget,
    );

    return getRequest(params, null, "contentImpression");
  }

  /**
   * @param {Node} node
   * @param {string} contentInteraction
   * @returns {string | undefined}
   */
  function buildContentInteractionRequestNode(node, contentInteraction) {
    if (!node) {
      return;
    }

    const contentNode = content.findParentContentNode(node);
    const contentBlock = content.buildContentBlock(contentNode);

    if (!contentBlock) {
      return;
    }

    if (!contentInteraction) {
      contentInteraction = "Unknown";
    }

    return buildContentInteractionRequest(
      contentInteraction,
      contentBlock.name,
      contentBlock.piece,
      contentBlock.target,
    );
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
   * Log the site search request
   *
   * @param {string} keyword
   * @param {string} category
   * @param {number} resultsCount
   * @param {object} [customData]
   */
  function logSiteSearch(keyword, category, resultsCount, customData) {
    const request = getRequest(
      "search=" +
        encodeURIComponent(keyword) +
        (category
          ? "&search_cat=" + encodeURIComponent(category)
          : "") +
        (h.isDefined(resultsCount) ? "&search_count=" + resultsCount : ""),
      customData,
      "sitesearch",
    );

    sendRequest(request, configTrackerPause);
  }

  /**
   * Log the goal with the server
   *
   * @param {string} idGoal
   * @param {string} customRevenue
   * @param {object} customData
   * @param {() => void} callback
   */
  function logGoal(idGoal, customRevenue, customData, callback) {
    const request = getRequest(
      "idgoal=" + idGoal + (customRevenue ? "&revenue=" + customRevenue : ""),
      customData,
      "goal",
    );

    sendRequest(request, configTrackerPause, callback);
  }

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
   * Browser prefix
   *
   * @param {string} prefix
   * @param {string} propertyName
   *
   * @returns {string}
   */
  function prefixPropertyName(prefix, propertyName) {
    if (prefix !== "") {
      return (
        prefix + propertyName.charAt(0).toUpperCase() + propertyName.slice(1)
      );
    }

    return propertyName;
  }

  /**
   * Check for pre-rendered web pages, and log the page view/link/goal
   * according to the configuration and/or visibility
   *
   * @see http://dvcs.w3.org/hg/webperf/raw-file/tip/specs/PageVisibility/Overview.html
   *
   * @param {() => void} callback
   */
  function trackCallback(callback) {
    var isPreRendered,
      i,
      // Chrome 13, IE10, FF10
      prefixes = ["", "webkit", "ms", "moz"],
      prefix;

    if (!configCountPreRendered) {
      for (i = 0; i < prefixes.length; i++) {
        prefix = prefixes[i];

        // does this browser support the page visibility API?
        if (
          Object.prototype.hasOwnProperty.call(
            document,
            prefixPropertyName(prefix, "hidden"),
          )
        ) {
          // if pre-rendered, then defer callback until page visibility changes
          if (
            document[
              prefixPropertyName(prefix, "visibilityState")
            ] === "prerender"
          ) {
            isPreRendered = true;
          }
          break;
        }
      }
    }

    if (isPreRendered) {
      // note: the event name doesn't follow the same naming convention as vendor properties
      document.addEventListener(
        prefix + "visibilitychange",
        function ready() {
          document.removeEventListener(
            prefix + "visibilitychange",
            ready,
            false,
          );
          callback();
        },
      );

      return;
    }

    // configCountPreRendered === true || isPreRendered === false
    callback();
  }

  /**
   * @returns {string}
   */
  function getCrossDomainVisitorId() {
    const visitorId = trackerInstance.getVisitorId();
    const deviceId = makeCrossDomainDeviceId();
    return visitorId + deviceId;
  }

  /**
   * This modifies the passed-in element!
   *
   * @param {Element} element
   */
  function replaceHrefForCrossDomainLink(element) {
    if (!element) {
      return;
    }

    if (!query.hasNodeAttribute(element, "href")) {
      return;
    }

    let link = query.getAttributeValueFromNode(element, "href");

    if (!link || startsUrlWithTrackerUrl(link)) {
      return;
    }

    if (!trackerInstance.getVisitorId()) {
      return; // cookies are disabled.
    }

    // we need to remove the parameter and add it again if needed to make sure we have latest timestamp
    // and visitorId (eg userId might be set etc)
    link = h.removeUrlParameter(link, configVisitorIdUrlParameter);

    const crossDomainVisitorId = getCrossDomainVisitorId();

    link = h.addUrlParameter(
      link,
      configVisitorIdUrlParameter,
      crossDomainVisitorId,
    );

    query.setAnyAttribute(element, "href", link);
  }

  /**
   * @param {HTMLLinkElement} element
   *
   * @returns {boolean}
   */
  function isLinkToDifferentDomainButSameEaveWebsite(element) {
    const targetLink = query.getAttributeValueFromNode(element, "href");

    if (!targetLink) {
      return false;
    }

    const url = new URL(targetLink);

    var isOutlink =
      targetLink.indexOf("//") === 0 ||
      targetLink.indexOf("http://") === 0 ||
      targetLink.indexOf("https://") === 0;

    if (!isOutlink) {
      return false;
    }

    const originalSourcePath = url.pathname || getPathName(element.href);
    const originalSourceHostName = (
      url.hostname || h.getHostName(element.href)
    ).toLowerCase();

    if (isSiteHostPath(originalSourceHostName, originalSourcePath)) {
      // we could also check against config cookie domain but this would require that other website
      // sets actually same cookie domain and we cannot rely on it.
      if (!h.isSameHost(domainAlias, h.domainFixup(originalSourceHostName))) {
        return true;
      }

      return false;
    }

    return false;
  }

  /**
   * Process clicks on button elements
   *
   * @param {HTMLElement} sourceElement
   */
  function processButtonClick(sourceElement) {
    // TODO improve data values passed...
    // fire event
    logEvent(
      "button",
      "click",
      "button click",
      sourceElement.innerText,
      null,
      null,
    );
  }

  /**
   * Process clicks on link elements
   *
   * @param {HTMLElement} sourceElement
   */
  function processLinkClick(sourceElement) {
    const link = getLinkIfShouldBeProcessed(sourceElement);
    if (link && link.type) {
      link.href = h.safeDecodeWrapper(link.href);
      logLink(link.href, link.type, undefined, sourceElement);
    }
  }

  /**
   * https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/button
   *
   * @param {MouseEvent} event
   *
   * @returns {string}
   */
  function getNameOfClickedMouseButton(event) {
    switch (event.button) {
      case 0:
        return "primary";
      case 1:
        return "aux";
      case 2:
        return "secondary";
      case 3:
        return "fourth";
      case 4:
        return "fifth";
      default:
        return "unknown";
    }
  }

  /**
   * @param {Event} event
   *
   * @returns {EventTarget | null}
   */
  function getTargetElementFromEvent(event) {
    return event.target;
  }

  /**
   * @param {string} nodeName
   *
   * @returns {boolean}
   */
  function isLinkNode(nodeName) {
    return nodeName === "A" || nodeName === "AREA";
  }

  /**
   * @param {string} nodeName
   *
   * @returns {boolean}
   */
  function isButtonNode(nodeName) {
    return nodeName === "BUTTON";
  }

  /**
   * Handle click event
   *
   * @param {boolean} enable
   *
   * @returns {(event: MouseEvent) => void}
   */
  function clickHandler(enable) {
    /*
      List of element tracking to check for in priority order.
      This click handler will only fire 1 event per click, so higher
      priority tracked elements should appear earlier in the list.

      e.g.
      linkTracking comes before buttonClickTracking.
      Therefore, we expect clicking on the button element of
      `<a href="..."><button>click!</button></a>`
      Will trigger a link click event rather than a button click event.
      */
      const trackers = [
      {
        trackingEnabled: () => linkTrackingEnabled,
        nodeFilter: isLinkNode,
        clickProcessor: processLinkClick,
      },
      {
        trackingEnabled: () => buttonClickTrackingEnabled,
        nodeFilter: isButtonNode,
        clickProcessor: processButtonClick,
      },
      {
        trackingEnabled: () => imageClickTrackingEnabled,
        nodeFilter: (nodeName) => nodeName === "IMG",
        clickProcessor: (sourceElement) =>
          logEvent(
            "click",
            "img",
            "img tag clicked",
            sourceElement.id,
            {
              src: sourceElement.src,
              full_html: sourceElement.outerHTML,
            },
            undefined,
          ),
      },
    ];
    var activeTracker;

    /**
     * From a click listener callback event, get a target element we
     * are tracking, if any.
     *
     * @param {Event} event h.addEventListener callback param
     */
    function getClickTarget(event) {
      const initialTarget = getTargetElementFromEvent(event);

      /*
        loop over all enabled element trackers, returning the first
        (aka highest priority) node found
        */
      let targetNode = undefined;
      var i;
      for (i = 0; i < trackers.length; i++) {
        const targetTrackingEnabled = trackers[i].trackingEnabled();
        const targetNodeFilter = trackers[i].nodeFilter;
        if (targetTrackingEnabled) {
          targetNode = getTargetNode(targetNodeFilter, initialTarget);
          if (targetNode) {
            // TODO: separate this side affect
            activeTracker = trackers[i];
            break;
          }
        }
      }
      return targetNode;
    }

    return function (event) {
      const target = getClickTarget(event);
      // we arent tracking the clicked element(s)
      if (!target || !activeTracker) {
        return;
      }

      const button = getNameOfClickedMouseButton(event);

      if (event.type === "click") {
        let ignoreClick = false;
        if (enable && button === "middle") {
          // if enabled, we track middle clicks via mouseup
          // some browsers (eg chrome) trigger click and mousedown/up events when middle is clicked,
          // whereas some do not. This way we make "sure" to track them only once, either in click
          // (default) or in mouseup (if enable == true)
          ignoreClick = true;
        }

        if (target && !ignoreClick) {
          activeTracker.clickProcessor(target);
        }
      } else if (event.type === "mousedown") {
        if (button === "middle" && target) {
          lastButton = button;
          lastTarget = target;
        } else {
          lastButton = null;
          lastTarget = null;
        }
      } else if (event.type === "mouseup") {
        if (button === lastButton && target === lastTarget) {
          activeTracker.clickProcessor(target);
        }
        lastButton = null;
        lastTarget = null;
      } else if (event.type === "contextmenu") {
        activeTracker.clickProcessor(target);
      }
    };
  }

  /**
   * Add click listener to a DOM element
   *
   * @param {Element} element
   * @param {boolean} enable
   * @param {boolean} useCapture
   */
  function addClickListener(element, enable, useCapture) {
    const enableType = typeof enable;
    if (enableType === "undefined") {
      enable = true;
    }

    element.addEventListener("click", clickHandler(enable), useCapture);

    if (enable) {
      element.addEventListener("mouseup", clickHandler(enable), useCapture);
      element.addEventListener(
        "mousedown",
        clickHandler(enable),
        useCapture,
      );
      element.addEventListener(
        "contextmenu",
        clickHandler(enable),
        useCapture,
      );
    }
  }

  /**
   * @param {boolean} checkOnScroll
   * @param {number} timeIntervalInMs
   * @param {any} tracker
   *
   * @returns {boolean | undefined}
   */
  function enableTrackOnlyVisibleContent(
    checkOnScroll,
    timeIntervalInMs,
    tracker,
  ) {
    if (isTrackOnlyVisibleContentEnabled) {
      // already enabled, do not register intervals again
      return true;
    }

    isTrackOnlyVisibleContentEnabled = true;

    let didScroll = false;
    let events;
    let index;

    function setDidScroll() {
      didScroll = true;
    }

    h.trackCallbackOnLoad(function () {
      function checkContent(intervalInMs) {
        setTimeout(function () {
          if (!isTrackOnlyVisibleContentEnabled) {
            return; // the tests stopped tracking only visible content
          }
          didScroll = false;
          tracker.trackVisibleContentImpressions();
          checkContent(intervalInMs);
        }, intervalInMs);
      }

      function checkContentIfDidScroll(intervalInMs) {
        setTimeout(function () {
          if (!isTrackOnlyVisibleContentEnabled) {
            return; // the tests stopped tracking only visible content
          }

          if (didScroll) {
            didScroll = false;
            tracker.trackVisibleContentImpressions();
          }

          checkContentIfDidScroll(intervalInMs);
        }, intervalInMs);
      }

      if (checkOnScroll) {
        // scroll event is executed after each pixel, so we make sure not to
        // execute event too often. otherwise FPS goes down a lot!
        events = ["scroll", "resize"];
        for (index = 0; index < events.length; index++) {
          window[events[index]].addEventListener(
            setDidScroll,
            false,
          );
        }

        checkContentIfDidScroll(100);
      }

      if (timeIntervalInMs && timeIntervalInMs > 0) {
        checkContent(timeIntervalInMs);
      }
    });
  }

  /*<DEBUG>*/
  /**
   * Register a test hook. Using eval() permits access to otherwise
   * privileged members.
   *
   * @param {string} hookName
   * @param {object | string} userHook
   *
   * @returns {object | null}
   */
  function registerHook(hookName, userHook) {
    let hookObj = null;

    if (
      h.isString(hookName) &&
      !h.isDefined(registeredHooks[hookName]) &&
      userHook
    ) {
      if (h.isObject(userHook)) {
        hookObj = userHook;
      } else if (h.isString(userHook)) {
        try {
          eval("hookObj =" + userHook);
        } catch (ignore) {
          // ignore
        }
      }

      registeredHooks[hookName] = hookObj;
    }

    return hookObj;
  }

  /*</DEBUG>*/

  /**
   * @typedef RequestQueue
   * @property {boolean} enabled
   * @property {string[]} requests
   * @property {number | null} timeout
   * @property {number} interval
   * @property {() => void} sendRequests
   * @property {() => boolean} canQueue
   * @property {(requests: string[]) => void} pushMultiple
   * @property {(requestUrl: string) => void} push
   */

  /** @type {RequestQueue} */
  const requestQueue = {
    enabled: true,
    requests: [],
    timeout: null,
    interval: 2500,
    sendRequests: function () {
      const requestsToTrack = this.requests;
      this.requests = [];
      if (requestsToTrack.length === 1) {
        sendRequest(requestsToTrack[0], configTrackerPause);
      } else {
        sendBulkRequest(requestsToTrack, configTrackerPause);
      }
    },
    canQueue: function () {
      return !eaveWindow.eave.isPageUnloading && this.enabled;
    },
    pushMultiple: function (requests) {
      if (!this.canQueue()) {
        sendBulkRequest(requests, configTrackerPause);
        return;
      }

      for (let i = 0; i < requests.length; i++) {
        this.push(requests[i]);
      }
    },
    push: function (requestUrl) {
      if (!requestUrl) {
        return;
      }
      if (!this.canQueue()) {
        // we don't queue as we need to ensure the request will be sent when the page is unloading...
        sendRequest(requestUrl, configTrackerPause);
        return;
      }

      requestQueue.requests.push(requestUrl);

      if (this.timeout) {
        clearTimeout(this.timeout);
        this.timeout = null;
      }
      // we always extend by another 2.5 seconds after receiving a tracking request
      // @ts-ignore - it's using the NodeJS setTimeout which returns a Timeout object, but we only need it to return a number.
      this.timeout = setTimeout(function () {
        requestQueue.timeout = null;
        requestQueue.sendRequests();
      }, requestQueue.interval);

      const trackerQueueId = "RequestQueue" + uniqueTrackerId;
      if (
        !Object.prototype.hasOwnProperty.call(
          eaveWindow.eave.plugins,
          trackerQueueId,
        )
      ) {
        // we setup one unload handler per tracker...
        // eave.addPlugin might not be defined at this point, we add the plugin directly also to make
        // JSLint happy.
        eaveWindow.eave.plugins[trackerQueueId] = {
          unload: function () {
            if (requestQueue.timeout) {
              clearTimeout(requestQueue.timeout);
            }
            requestQueue.sendRequests();
          },
        };
      }
    },
  };
  /************************************************************
   * Constructor
   ************************************************************/

  /*
   * initialize tracker
   */

  /*<DEBUG>*/
  /*
   * initialize test plugin
   */
  h.executePluginMethod("run", null, registerHook);
  /*</DEBUG>*/

  /************************************************************
   * Public data and methods
   ************************************************************/

  /*<DEBUG>*/
  /*
   * Test hook accessors
   */
  this.hook = registeredHooks;

  /**
   * @param {string} hookName
   *
   * @returns {object}
   */
  this.getHook = function (hookName) {
    return registeredHooks[hookName];
  };

  /**
   * @returns {object} the `query` import
   */
  this.getQuery = function () {
    return query;
  };

  /**
   * @returns {object} the `content` import
   */
  this.getContent = function () {
    return content;
  };

  /**
   * @returns {boolean}
   */
  this.isUsingAlwaysUseSendBeacon = function () {
    return configAlwaysUseSendBeacon;
  };

  /**
   * @param {string} contentName
   * @param {any} contentPiece
   * @param {any} contentTarget
   *
   * @returns {string}
   */
  this.buildContentImpressionRequest = buildContentImpressionRequest;

  /**
   * @param {any} interaction
   * @param {string} name
   * @param {any} piece
   * @param {any} target
   *
   * @returns {string | undefined}
   */
  this.buildContentInteractionRequest = buildContentInteractionRequest;

  /**
   * @param {Element} node
   * @param {string} contentInteraction
   *
   * @returns {string | undefined}
   */
  this.buildContentInteractionRequestNode = buildContentInteractionRequestNode;

  /**
   * Log all content pieces
   *
   * @param {Element[]} contentNodes
   *
   * @returns {string[]}
   */
  this.getContentImpressionsRequestsFromNodes = getContentImpressionsRequestsFromNodes;

  /**
   * Log currently visible content pieces
   *
   * @param {Element[]} contentNodes
   *
   * @returns {string[]}
   */
  this.getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet = getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet;

  /**
   * @param {() => void} callback
   */
  this.trackCallbackOnLoad = h.trackCallbackOnLoad;

  /**
   * @param {() => void} callback
   */
  this.trackCallbackOnReady = h.trackCallbackOnReady;

  /**
   * Log all content pieces
   *
   * @param {any} contents
   * @param {Element[]} contentNodes
   *
   * @returns {string[]}
   */
  this.buildContentImpressionsRequests = buildContentImpressionsRequests;

  /**
   * @param {any} contentBlock
   *
   * @returns {boolean}
   */
  this.wasContentImpressionAlreadyTracked = wasContentImpressionAlreadyTracked;

  /**
   * @param {Element} anyNode
   * @param {any} interaction
   * @param {any} fallbackTarget
   *
   * @returns {string | undefined}
   */
  this.appendContentInteractionToRequestIfPossible = getContentInteractionToRequestIfPossible;

  /**
   * @param {Element[]} contentNodes
   */
  this.setupInteractionsTracking = setupInteractionsTracking;

  /**
   * @param {Element} targetNode
   *
   * @returns {boolean | string | undefined}
   */
  this.trackContentImpressionClickInteraction = trackContentImpressionClickInteraction;

  /**
   * @param {HTMLElement} node
   *
   * @returns {boolean}
   */
  this.internalIsNodeVisible = isVisible;

  /**
   * @param {Element} contentNode
   * @param {Element} interactedNode
   *
   * @returns {boolean}
   */
  this.isNodeAuthorizedToTriggerInteraction = isNodeAuthorizedToTriggerInteraction;

  /**
   * @returns {string[]}
   */
  this.getDomains = function () {
    return configHostsAlias;
  };

  /**
   * @returns {string[]}
   */
  this.getExcludedReferrers = function () {
    return configExcludedReferrers;
  };

  /**
   * @returns {string}
   */
  this.getConfigIdPageView = function () {
    return configIdPageView;
  };

  /**
   * @returns {string[]}
   */
  this.getConfigDownloadExtensions = function () {
    return configDownloadExtensions;
  };

  /**
   * @param {boolean} checkOnScroll
   * @param {number} timeIntervalInMs
   *
   * @returns {boolean | undefined}
   */
  this.enableTrackOnlyVisibleContent = function (
    checkOnScroll,
    timeIntervalInMs,
  ) {
    return enableTrackOnlyVisibleContent(checkOnScroll, timeIntervalInMs, this);
  };

  /**
   * @noreturn
   */
  this.clearTrackedContentImpressions = function () {
    trackedContentImpressions = [];
  };

  /**
   * @returns {unknown[]}
   */
  this.getTrackedContentImpressions = function () {
    return trackedContentImpressions;
  };

  /**
   * @noreturn
   */
  this.clearEnableTrackOnlyVisibleContent = function () {
    isTrackOnlyVisibleContentEnabled = false;
  };

  /**
   * @noreturn
   */
  this.disableLinkTracking = function () {
    clickListenerInstalled = false;
    linkTrackingEnabled = false;
  };

  /**
   * @returns {string}
   */
  this.getCustomPagePerformanceTiming = function () {
    return customPagePerformanceTiming;
  };

  /**
   * @noreturn
   */
  this.removeAllAsyncTrackersButFirst = function () {
    const firstTracker = eaveWindow.eave.asyncTrackers[0];
    eaveWindow.eave.asyncTrackers = [firstTracker];
  };

  /**
   * @returns {string[]}
   */
  this.getConsentRequestsQueue = function () {
    let i;
    const requests = [];

    for (i = 0; i < consentRequestsQueue.length; i++) {
      requests.push(consentRequestsQueue[i][0]);
    }

    return requests;
  };

  /**
   * @returns {RequestQueue}
   */
  this.getRequestQueue = function () {
    return requestQueue;
  };

  /**
   * @returns {Error[]}
   */
  this.getJavascriptErrors = function () {
    return javaScriptErrors;
  };

  /**
   * @noreturn
   */
  this.unsetPageIsUnloading = function () {
    eaveWindow.eave.isPageUnloading = false;
  };

  /*</DEBUG>*/
  /**
   * @returns {boolean}
   */
  this.hasConsent = function () {
    return configHasConsent;
  };

  /**
   * Get visitor ID (from first party cookie)
   *
   * @returns {string} Visitor ID in hexits (or empty string, if not yet known)
   */
  this.getVisitorId = function () {
    return cookieManager.getCookie(cookieManager.VISITOR_ID_COOKIE_NAME) || "";
  };

  /**
   * Get the time at which the referrer (used for Goal Attribution) was detected
   *
   * @returns {string | number} Timestamp or 0 if no referrer currently set
   */
  function getAttributionReferrerTimestamp() {
    return cookieManager.getCookie(configReferralTimestampKey) || 0;
  }

  /**
   * @type {() => string | number}
   */
  this.getAttributionReferrerTimestamp = getAttributionReferrerTimestamp;

  /**
   * Get the full referrer URL that will be used for Goal Attribution
   *
   * @returns {string} Raw URL, or empty string '' if no referrer currently set
   */
  function getAttributionReferrerUrl() {
    return cookieManager.getCookie(configReferralUrlKey) || "";
  }

  /**
   * @type {() => string}
   */
  this.getAttributionReferrerUrl = getAttributionReferrerUrl;

  /**
   * Get referrer URL query params.
   *
   * @returns {object} map of query param keys and values
   */
  function getAttributionReferrerQueryParams() {
    return cookieManager.getCookie(configReferralQueryParamsKey) || {};
  }

  /**
   * @type {() => object}
   */
  this.getAttributionReferrerQueryParams = getAttributionReferrerQueryParams;

  /**
   * Specify the eave client ID for the specific customer.
   * This value is needed to authenticate requests to send atoms,
   * so it is vital!
   *
   * @param {string} clientId
   *
   * @noreturn
   */
  this.setEaveClientId = function (clientId) {
    eaveClientId = clientId;
  };

  /**
   * Specify the eave tracking URL
   *
   * @param {string} trackerUrl
   *
   * @noreturn
   */
  this.setTrackerUrl = function (trackerUrl) {
    configTrackerUrl = trackerUrl;
  };

  /**
   * Returns the eave tracking URL
   *
   * @returns {string}
   */
  this.getTrackerUrl = function () {
    return configTrackerUrl;
  };

  /**
   * Returns the eave server URL.
   *
   * @returns {string}
   */
  this.getEaveUrl = function () {
    // TODO: we could hardcode this?
    return this.getTrackerUrl();
  };

  /**
   * Adds a new tracker. All sent requests will be also sent to the given siteId and eaveUrl.
   *
   * @param {string} eaveUrl  The tracker URL of the current tracker instance
   * @param {number} siteId
   *
   * @returns {Tracker}
   */
  this.addTracker = function (eaveUrl, siteId) {
    if (!h.isDefined(eaveUrl) || null === eaveUrl) {
      eaveUrl = this.getTrackerUrl();
    }

    const tracker = new Tracker(eaveUrl, siteId);

    eaveWindow.eave.asyncTrackers.push(tracker);

    eaveWindow.eave.tracker.trigger("TrackerAdded", [this]);

    return tracker;
  };

  // /**
  //  * Returns the site ID
  //  *
  //  * @returns {number}
  //  */
  // this.getSiteId = function () {
  //   return configTrackerSiteId;
  // };

  // /**
  //  * Specify the site ID
  //  *
  //  * @param {int|string} siteId
  //  */
  // this.setSiteId = function (siteId) {
  //   setSiteId(siteId);
  // };

  /**
   * Pass custom data to the server
   *
   * Examples:
   *   tracker.setCustomData(object);
   *   tracker.setCustomData(key, value);
   *
   * @param {object} key_or_obj
   * @param {unknown} opt_value
   * @noreturn
   */
  this.setCustomData = function (key_or_obj, opt_value) {
    if (h.isObject(key_or_obj)) {
      configCustomData = key_or_obj;
    } else {
      if (!configCustomData) {
        configCustomData = {};
      }
      configCustomData[key_or_obj] = opt_value;
    }
  };

  /**
   * Get custom data
   *
   * @returns {object}
   */
  this.getCustomData = function () {
    return configCustomData;
  };

  /**
   * Configure function with custom request content processing logic.
   * It gets called after request content in form of query parameters string has been prepared and before request content gets sent.
   *
   * Examples:
   *   tracker.setCustomRequestProcessing(function(request){
   *     let pairs = request.split('&');
   *     let result = {};
   *     pairs.forEach(function(pair) {
   *       pair = pair.split('=');
   *       result[pair[0]] = decodeURIComponent(pair[1] || '');
   *     });
   *     return JSON.stringify(result);
   *   });
   *
   * @param {Function} customRequestContentProcessingLogic
   */
  this.setCustomRequestProcessing = function (
    customRequestContentProcessingLogic,
  ) {
    configCustomRequestContentProcessing = customRequestContentProcessingLogic;
  };

  /**
   * Appends the specified query string to the Tracking API URL
   *
   * @param {string} queryString eg. 'lat=140&long=100'
   * @noreturn
   */
  this.appendToTrackingUrl = function (queryString) {
    configAppendToTrackingUrl = queryString;
  };

  /**
   * Returns the query string for the current HTTP Tracking API request.
   * eave would prepend the hostname and path to eave: http://example.org/eave/api?
   * prior to sending the request.
   *
   * @param request eg. "param=value&param2=value2"
   * @returns {string}
   */
  this.getRequest = function (request) {
    return getRequest(request);
  };

  /**
   * Add plugin defined by a name and a callback function.
   * The callback function will be called whenever a tracking request is sent.
   * This can be used to append data to the tracking request, or execute other custom logic.
   *
   * @param {string} pluginName
   * @param {Object} pluginObj
   *
   * @noreturn
   */
  this.addPlugin = function (pluginName, pluginObj) {
    eaveWindow.eave.plugins[pluginName] = pluginObj;
  };

  /**
   * Lazy loads the custom variables from the cookie, only once during this page view
   *
   * @noreturn
   */
  function loadCustomVariables() {
    if (customVariables === false) {
      customVariables = cookieManager.getCustomVariablesFromCookie();
    }
  }

  /**
   * Set Custom Dimensions. Set Custom Dimensions will not be cleared after a tracked pageview and will
   * be sent along all following tracking requests. It is possible to remove/clear a value via `deleteCustomDimension`.
   *
   * @param {number} customDimensionId A Custom Dimension index
   * @param {string} value
   *
   * @noreturn
   */
  this.setCustomDimension = function (customDimensionId, value) {
    if (customDimensionId > 0) {
      if (!h.isDefined(value)) {
        value = "";
      }
      if (!h.isString(value)) {
        value = String(value);
      }
      customDimensions[customDimensionId] = value;
    }
  };

  /**
   * Get a stored value for a specific Custom Dimension index.
   *
   * @param {number} customDimensionId A Custom Dimension index
   * @returns {object}
   */
  this.getCustomDimension = function (customDimensionId) {
    if (
      customDimensionId > 0 &&
      Object.prototype.hasOwnProperty.call(customDimensions, customDimensionId)
    ) {
      return customDimensions[customDimensionId];
    }
  };

  /**
   * Delete a custom dimension.
   *
   * @param {number} customDimensionId Custom dimension Id
   * @noreturn
   */
  this.deleteCustomDimension = function (customDimensionId) {
    if (customDimensionId > 0) {
      delete customDimensions[customDimensionId];
    }
  };

  /**
   * Set custom variable within this visit
   *
   * @param {number} index Custom variable slot ID from 1-5
   * @param {string} name
   * @param {string} value
   * @param {string | number} scope Scope of Custom Variable:
   *                     - "visit" will store the name/value in the visit and will persist it in the cookie for the duration of the visit,
   *                     - "page" will store the name/value in the next page view tracked.
   *                     - "event" will store the name/value in the next event tracked.
   *
   * @noreturn
   */
  this.setCustomVariable = function (index, name, value, scope) {
    var toRecord;

    if (!h.isDefined(scope)) {
      scope = "visit";
    }
    if (!h.isDefined(name)) {
      return;
    }
    if (!h.isDefined(value)) {
      value = "";
    }
    if (index > 0) {
      name = !h.isString(name) ? String(name) : name;
      value = !h.isString(value) ? String(value) : value;
      toRecord = [
        name.slice(0, customVariableMaximumLength),
        value.slice(0, customVariableMaximumLength),
      ];
      // numeric scope is there for GA compatibility
      if (scope === "visit" || scope === 2) {
        loadCustomVariables();
        customVariables[index] = toRecord;
      } else if (scope === "page" || scope === 3) {
        customVariablesPage[index] = toRecord;
      } else if (scope === "event") {
        /* GA does not have 'event' scope but we do */
        customVariablesEvent[index] = toRecord;
      }
    }
  };

  /**
   * Get custom variable
   *
   * @param {number} index Custom variable slot ID from 1-5
   * @param {string | number} scope Scope of Custom Variable: "visit" or "page" or "event"
   *
   * @returns {unknown | boolean}
   */
  this.getCustomVariable = function (index, scope) {
    var cvar;

    if (!h.isDefined(scope)) {
      scope = "visit";
    }

    if (scope === "page" || scope === 3) {
      cvar = customVariablesPage[index];
    } else if (scope === "event") {
      cvar = customVariablesEvent[index];
    } else if (scope === "visit" || scope === 2) {
      loadCustomVariables();
      cvar = customVariables[index];
    }

    if (!h.isDefined(cvar) || (cvar && cvar[0] === "")) {
      return false;
    }

    return cvar;
  };

  /**
   * Delete custom variable
   *
   * @param {number} index Custom variable slot ID from 1-5
   * @param {string} scope
   * @noreturn
   */
  this.deleteCustomVariable = function (index, scope) {
    // Only delete if it was there already
    if (this.getCustomVariable(index, scope)) {
      this.setCustomVariable(index, "", "", scope);
    }
  };

  /**
   * Deletes all custom variables for a certain scope.
   *
   * @param {string | number} scope
   * @noreturn
   */
  this.deleteCustomVariables = function (scope) {
    if (scope === "page" || scope === 3) {
      customVariablesPage = {};
    } else if (scope === "event") {
      customVariablesEvent = {};
    } else if (scope === "visit" || scope === 2) {
      customVariables = {};
    }
  };

  /**
   * When called then the Custom Variables of scope "visit" will be stored (persisted) in a first party cookie
   * for the duration of the visit. This is useful if you want to call getCustomVariable later in the visit.
   *
   * By default, Custom Variables of scope "visit" are not stored on the visitor's computer.
   *
   * @noreturn
   */
  this.storeCustomVariablesInCookie = function () {
    configStoreCustomVariablesInCookie = true;
  };

  /**
   * Set delay for link tracking (in milliseconds)
   *
   * @param {number} delay Delay [ms]
   *
   * @noreturn
   */
  this.setLinkTrackingTimer = function (delay) {
    configTrackerPause = delay;
  };

  /**
   * Get delay for link tracking (in milliseconds)
   *
   * @returns {number} Delay [ms]
   */
  this.getLinkTrackingTimer = function () {
    return configTrackerPause;
  };

  /**
   * Set list of file extensions to be recognized as downloads
   *
   * @param {string | string[]} extensions
   *
   * @noreturn
   */
  this.setDownloadExtensions = function (extensions) {
    if (typeof extensions === "string") {
      extensions = extensions.split("|");
    }
    configDownloadExtensions = extensions;
  };

  /**
   * Specify additional file extensions to be recognized as downloads
   *
   * @param {string | string[]} extensions  for example 'custom' or ['custom1','custom2','custom3']
   *
   * @noreturn
   */
  this.addDownloadExtensions = function (extensions) {
    var i;
    if (typeof extensions === "string") {
      extensions = extensions.split("|");
    }
    for (i = 0; i < extensions.length; i++) {
      configDownloadExtensions.push(extensions[i]);
    }
  };

  /**
   * Removes specified file extensions from the list of recognized downloads
   *
   * @param {string | string[]} extensions  for example 'custom' or ['custom1','custom2','custom3']
   *
   * @noreturn
   */
  this.removeDownloadExtensions = function (extensions) {
    var i,
      newExtensions = [];
    if (typeof extensions === "string") {
      extensions = extensions.split("|");
    }
    for (i = 0; i < configDownloadExtensions.length; i++) {
      if (h.indexOfArray(extensions, configDownloadExtensions[i]) === -1) {
        newExtensions.push(configDownloadExtensions[i]);
      }
    }
    configDownloadExtensions = newExtensions;
  };

  /**
   * Set array of domains to be treated as local. Also supports path, eg '.eave.org/subsite1'. In this
   * case all links that don't go to '*.eave.org/subsite1/ *' would be treated as outlinks.
   * For example a link to 'eave.org/' or 'eave.org/subsite2' both would be treated as outlinks.
   *
   * Also supports page wildcard, eg 'eave.org/index*'. In this case all links
   * that don't go to eave.org/index* would be treated as outlinks.
   *
   * The current domain will be added automatically if no given host alias contains a path and if no host
   * alias is already given for the current host alias. Say you are on "example.org" and set
   * "hostAlias = ['example.com', 'example.org/test']" then the current "example.org" domain will not be
   * added as there is already a more restrictive hostAlias 'example.org/test' given. We also do not add
   * it automatically if there was any other host specifying any path like
   * "['example.com', 'example2.com/test']". In this case we would also not add the current
   * domain "example.org" automatically as the "path" feature is used. As soon as someone uses the path
   * feature, for eave JS Tracker to work correctly in all cases, one needs to specify all hosts
   * manually.
   *
   * @param {string | string[]} hostsAlias
   *
   * @noreturn
   */
  this.setDomains = function (hostsAlias) {
    configHostsAlias = typeof hostsAlias === "string" ? [hostsAlias] : hostsAlias;

    let hasDomainAliasAlready = false,
      i = 0,
      alias;
    for (i; i < configHostsAlias.length; i++) {
      alias = String(configHostsAlias[i]);

      if (h.isSameHost(domainAlias, h.domainFixup(alias))) {
        hasDomainAliasAlready = true;
        break;
      }

      const pathName = getPathName(alias);
      if (pathName && pathName !== "/" && pathName !== "/*") {
        hasDomainAliasAlready = true;
        break;
      }
    }

    // The current domain will be added automatically if no given host alias contains a path
    // and if no host alias is already given for the current host alias.
    if (!hasDomainAliasAlready) {
      /**
       * eg if domainAlias = 'eave.org' and someone set hostsAlias = ['eave.org/foo'] then we should
       * not add eave.org as it would increase the allowed scope.
       */
      configHostsAlias.push(domainAlias);
    }
  };

  /**
   * Set array of domains to be excluded as referrer. Also supports path, eg '.eave.org/subsite1'. In this
   * case all referrers that don't match '*.eave.org/subsite1/ *' would still be used as referrer.
   * For example 'eave.org/' or 'eave.org/subsite2' would both be used as referrer.
   *
   * Also supports page wildcard, eg 'eave.org/index*'. In this case all referrers
   * that don't match eave.org/index* would still be treated as referrer.
   *
   * Domains added with setDomains will automatically be excluded as referrers.
   *
   * @param {string | string[]} excludedReferrers
   *
   * @noreturn
   */
  this.setExcludedReferrers = function (excludedReferrers) {
    configExcludedReferrers = typeof excludedReferrers === "string"
      ? [excludedReferrers]
      : excludedReferrers;
  };

  /**
   * Enables cross domain linking. By default, the visitor ID that identifies a unique visitor is stored in
   * the browser's first party cookies. This means the cookie can only be accessed by pages on the same domain.
   * If you own multiple domains and would like to track all the actions and pageviews of a specific visitor
   * into the same visit, you may enable cross domain linking. Whenever a user clicks on a link it will append
   * a URL parameter pk_vid to the clicked URL which consists of these parts: 16 char visitorId, a 10 character
   * current timestamp and the last 6 characters are an id based on the userAgent to identify the users device).
   * This way the current visitorId is forwarded to the page of the different domain.
   *
   * On the different domain, the eave tracker will recognize the set visitorId from the URL parameter and
   * reuse this parameter if the page was loaded within 45 seconds. If cross domain linking was not enabled,
   * it would create a new visit on that page because we wouldn't be able to access the previously created
   * cookie. By enabling cross domain linking you can track several different domains into one website and
   * won't lose for example the original referrer.
   *
   * To make cross domain linking work you need to set which domains should be considered as your domains by
   * calling the method "setDomains()" first. We will add the URL parameter to links that go to a
   * different domain but only if the domain was previously set with "setDomains()" to make sure not to append
   * the URL parameters when a link actually goes to a third-party URL.
   *
   * @noreturn
   */
  this.enableCrossDomainLinking = function () {
    crossDomainTrackingEnabled = true;
  };

  /**
   * Disable cross domain linking if it was previously enabled. See enableCrossDomainLinking();
   *
   * @noreturn
   */
  this.disableCrossDomainLinking = function () {
    crossDomainTrackingEnabled = false;
  };

  /**
   * Detect whether cross domain linking is enabled or not. See enableCrossDomainLinking();
   *
   * @returns {boolean}
   */
  this.isCrossDomainLinkingEnabled = function () {
    return crossDomainTrackingEnabled;
  };

  /**
   * Returns the query parameter appended to link URLs so cross domain visits
   * can be detected.
   *
   * If your application creates links dynamically, then you'll have to add this
   * query parameter manually to those links (since the JavaScript tracker cannot
   * detect when those links are added).
   *
   * Eg:
   *
   * let url = 'http://myotherdomain.com/?' + eaveTracker.getCrossDomainLinkingUrlParameter();
   * $element.append('<a href="' + url + '"/>');
   *
   * @returns {string}
   */
  this.getCrossDomainLinkingUrlParameter = function () {
    return (
      encodeURIComponent(configVisitorIdUrlParameter) +
      "=" +
      encodeURIComponent(getCrossDomainVisitorId())
    );
  };

  /**
   * Set array of classes to be ignored if present in link
   *
   * @param {string | string[]} ignoreClasses
   *
   * @noreturn
   */
  this.setIgnoreClasses = function (ignoreClasses) {
    configIgnoreClasses = typeof ignoreClasses === "string"
      ? [ignoreClasses]
      : ignoreClasses;
  };

  /**
   * Set request method. If you specify GET then it will automatically disable sendBeacon.
   *
   * @param {string} method GET or POST; default is GET
   *
   * @noreturn
   */
  this.setRequestMethod = function (method) {
    if (method) {
      configRequestMethod = String(method).toUpperCase();
    } else {
      configRequestMethod = defaultRequestMethod;
    }

    if (configRequestMethod === "GET") {
      // send beacon always sends a POST request so we have to disable it to make GET work
      this.disableAlwaysUseSendBeacon();
    }
  };

  /**
   * Set request Content-Type header value, applicable when POST request method is used for submitting tracking events.
   * See XMLHttpRequest Level 2 spec, section 4.7.2 for invalid headers
   * @link http://dvcs.w3.org/hg/xhr/raw-file/tip/Overview.html
   *
   * @param {string} requestContentType; default is 'application/x-www-form-urlencoded; charset=UTF-8'
   *
   * @noreturn
   */
  this.setRequestContentType = function (requestContentType) {
    configRequestContentType = requestContentType || defaultRequestContentType;
  };

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
   * Returns the current url of the page that is currently being visited.
   *
   * @returns {string}
   */
  function getCurrentUrl() {
    return h.urlFixup(
      document.domain,
      window.location.href,
      h.getReferrer(),
    )[1];
  }

  /** @type {() => string} */
  this.getCurrentUrl = getCurrentUrl;

  /**
   * Override document.title
   *
   * @param {string} title
   *
   * @noreturn
   */
  this.setDocumentTitle = function (title) {
    configTitle = title;
  };

  /**
   * Override PageView id for every use of logPageView(). Do not use this if you call trackPageView()
   * multiple times during tracking (if, for example, you are tracking a single page application).
   *
   * @param {string} pageView
   *
   * @noreturn
   */
  this.setPageViewId = function (pageView) {
    configIdPageView = pageView;
    configIdPageViewSetManually = true;
  };

  /**
   * Returns the PageView id. If the id was manually set using setPageViewId(), that id will be returned.
   * If the id was not set manually, the id that was automatically generated in last trackPageView() will be
   * returned. If there was no last page view, this will be undefined.
   *
   * @returns {string}
   */
  this.getPageViewId = function () {
    return configIdPageView;
  };

  /**
   * Set array of classes to be treated as downloads
   *
   * @param {string | string[]} downloadClasses
   *
   * @noreturn
   */
  this.setDownloadClasses = function (downloadClasses) {
    configDownloadClasses = typeof downloadClasses === "string"
      ? [downloadClasses]
      : downloadClasses;
  };

  /**
   * Set an array of query parameters to be excluded if in the url
   *
   * @param {string | string[]} excludedQueryParams  'uid' or ['uid', 'sid']
   *
   * @noreturn
   */
  this.setExcludedQueryParams = function (excludedQueryParams) {
    configExcludedQueryParams = typeof excludedQueryParams === "string"
      ? [excludedQueryParams]
      : excludedQueryParams;
  };

  /**
   * Disables all cookies from being set
   *
   * Existing cookies will be deleted on the next call to track
   *
   * @noreturn
   */
  this.disableCookies = function () {
    cookieManager.configCookiesDisabled = true;

    if (configTrackerSiteId) {
      cookieManager.deleteEaveCookies();
    }
  };

  /**
   * Detects if cookies are enabled or not
   *
   * @returns {boolean}
   */
  this.areCookiesEnabled = function () {
    return !cookieManager.configCookiesDisabled;
  };

  /**
   * Enables cookies if they were disabled previously.
   *
   * @noreturn
   */
  this.setCookieConsentGiven = function () {
    if (cookieManager.configCookiesDisabled && !configDoNotTrack) {
      cookieManager.configCookiesDisabled = false;
      if (!configBrowserFeatureDetection) {
        this.enableBrowserFeatureDetection();
      }
      if (configTrackerSiteId && hasSentTrackingRequestYet) {
        cookieManager.setVisitorId();

        // sets attribution cookie, and updates visitorId in the backend
        // because hasSentTrackingRequestYet=true we assume there might not be another tracking
        // request within this page view so we trigger one ourselves.
        // if no tracking request has been sent yet, we don't set the attribution cookie cause eave
        // sets the cookie only when there is a tracking request. It'll be set if the user sends
        // a tracking request afterwards
        const request = getRequest("ping=1", null, "ping");
        sendRequest(request, configTrackerPause);
      }
    }
  };

  /**
   * Check first-party cookies and update the <code>configHasConsent</code> value.  Ensures that any
   * change to the user opt-in/out status in another browser window will be respected.
   *
   * @noreturn
   */
  function refreshConsentStatus() {
    if (cookieManager.getCookie(cookieManager.CONSENT_REMOVED_COOKIE_NAME)) {
      configHasConsent = false;
    } else if (cookieManager.getCookie(cookieManager.CONSENT_COOKIE_NAME)) {
      configHasConsent = true;
    }
  }

  /**
   * When called, no cookies will be set until you have called `setCookieConsentGiven()`
   * unless consent was given previously AND you called {@link rememberCookieConsentGiven()} when the user
   * gave consent.
   *
   * This may be useful when you want to implement for example a popup to ask for cookie consent.
   * Once the user has given consent, you should call {@link setCookieConsentGiven()}
   * or {@link rememberCookieConsentGiven()}.
   *
   * If you require tracking consent for example because you are tracking personal data and GDPR applies to you,
   * then have a look at `settings.push(['requireConsent'])` instead.
   *
   * If the user has already given consent in the past, you can either decide to not call `requireCookieConsent` at all
   * or call `settings.push(['setCookieConsentGiven'])` on each page view at any time after calling `requireCookieConsent`.
   *
   * When the user gives you the consent to set cookies, you can also call `settings.push(['rememberCookieConsentGiven', optionalTimeoutInHours])`
   * and for the duration while the cookie consent is remembered, any call to `requireCoookieConsent` will be automatically ignored
   * until you call `forgetCookieConsentGiven`.
   * `forgetCookieConsentGiven` needs to be called when the user removes consent for using cookies. This means if you call `rememberCookieConsentGiven` at the
   * time the user gives you consent, you do not need to ever call `settings.push(['setCookieConsentGiven'])` as the consent
   * will be detected automatically through cookies.
   *
   * @returns {boolean}
   */
  this.requireCookieConsent = function () {
    if (this.getRememberedCookieConsent()) {
      return false;
    }
    this.disableCookies();
    return true;
  };

  /**
   * If the user has given cookie consent previously and this consent was remembered, it will return the number
   * in milliseconds since 1970/01/01 which is the date when the user has given cookie consent. Please note that
   * the returned time depends on the users local time which may not always be correct.
   *
   * @returns {string | undefined}
   */
  this.getRememberedCookieConsent = function () {
    return cookieManager.getCookie(cookieManager.COOKIE_CONSENT_COOKIE_NAME);
  };

  /**
   * Calling this method will remove any previously given cookie consent and it disables cookies for subsequent
   * page views. You may call this method if the user removes cookie consent manually, or if you
   * want to re-ask for cookie consent after a specific time period.
   *
   * @noreturn
   */
  this.forgetCookieConsentGiven = function () {
    cookieManager.deleteCookie(
      cookieManager.COOKIE_CONSENT_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );
    this.disableCookies();
  };

  /**
   * Calling this method will remember that the user has given cookie consent across multiple requests by setting
   * a cookie named "_eave_cookie_consent". You can optionally define the lifetime of that cookie in hours
   * using a parameter.
   *
   * When you call this method, we imply that the user has given cookie consent for this page view, and will also
   * imply consent for all future page views unless the cookie expires or the user
   * deletes all their cookies. Remembering cookie consent means even if you call {@link disableCookies()},
   * then cookies will still be enabled and it won't disable cookies since the user has given consent for cookies.
   *
   * Please note that this feature requires you to set the `cookieDomain` and `cookiePath` correctly. Please
   * also note that when you call this method, consent will be implied for all sites that match the configured
   * cookieDomain and cookiePath. Depending on your website structure, you may need to restrict or widen the
   * scope of the cookie domain/path to ensure the consent is applied to the sites you want.
   *
   * @param {number} hoursToExpire After how many hours the cookie consent should expire. By default the consent is valid
   *                          for 30 years unless cookies are deleted by the user or the browser prior to this
   *
   * @noreturn
   */
  this.rememberCookieConsentGiven = function (hoursToExpire) {
    if (hoursToExpire) {
      // convert hours to ms
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      // 30 years ms
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }
    this.setCookieConsentGiven();
    const now = new Date().getTime();
    cookieManager.setCookie(
      cookieManager.COOKIE_CONSENT_COOKIE_NAME,
      String(now),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
  };

  /**
   * One off cookies clearing. Useful to call this when you know for sure a new visitor is using the same browser,
   * it maybe helps to "reset" tracking cookies to prevent data reuse for different users.
   *
   * @noreturn
   */
  this.deleteCookies = function () {
    cookieManager.deleteEaveCookies();
  };

  /**
   * Handle do-not-track requests
   *
   * @param {boolean} enable If true, don't track if user agent sends 'do-not-track' header
   *
   * @noreturn
   */
  this.setDoNotTrack = function (enable) {
    var dnt = navigator.doNotTrack;
    configDoNotTrack = enable && (dnt === "yes" || dnt === "1");

    // do not track also disables cookies and deletes existing cookies
    if (configDoNotTrack) {
      this.disableCookies();
    }
  };

  /**
   * Prevent campaign parameters being sent to the tracker, unless consent given.
   *
   * @noreturn
   */
  this.disableCampaignParameters = function () {
    configEnableCampaignParameters = false;
  };

  /**
   * Allow campaign parameters to be sent to the tracker.
   *
   * @noreturn
   */
  this.enableCampaignParameters = function () {
    configEnableCampaignParameters = true;
  };

  /**
   * Enables send beacon usage instead of regular XHR which reduces the link tracking time to a minimum
   * of 100ms instead of 500ms (default). This means when a user clicks for example on an outlink, the
   * navigation to this page will happen 400ms faster.
   * In case you are setting a callback method when issuing a tracking request, the callback method will
   *  be executed as soon as the tracking request was sent through "sendBeacon" and not after the tracking
   *  request finished as it is not possible to find out when the request finished.
   * Send beacon will only be used if the browser actually supports it.
   *
   * @noreturn
   */
  this.alwaysUseSendBeacon = function () {
    configAlwaysUseSendBeacon = true;
  };

  /**
   * Disables send beacon usage instead and instead enables using regular XHR when possible. This makes
   * callbacks work and also tracking requests will appear in the browser developer tools console.
   *
   * @noreturn
   */
  this.disableAlwaysUseSendBeacon = function () {
    configAlwaysUseSendBeacon = false;
  };

  /**
   * Add click listener to a specific link element.
   * When clicked, eave will log the click automatically.
   *
   * @param {Element} element
   * @param {boolean} enable If false, do not use pseudo click-handler (middle click + context menu)
   * @noreturn
   */
  this.addListener = function (element, enable) {
    addClickListener(element, enable, false);
  };

  /**
   * Install link tracker.
   *
   * If you change the DOM of your website or web application eave will automatically detect links
   * that were added newly.
   *
   * The default behaviour is to use actual click events. However, some browsers
   * (e.g., Firefox, Opera, and Konqueror) don't generate click events for the middle mouse button.
   *
   * To capture more "clicks", the pseudo click-handler uses mousedown + mouseup events.
   * This is not industry standard and is vulnerable to false positives (e.g., drag events).
   *
   * There is a Safari/Chrome/Webkit bug that prevents tracking requests from being sent
   * by either click handler.  The workaround is to set a target attribute (which can't
   * be "_self", "_top", or "_parent").
   *
   * @see https://bugs.webkit.org/show_bug.cgi?id=54783
   *
   * @param {boolean} enable Defaults to true.
   *                    * If "true", use pseudo click-handler (treat middle click and open contextmenu as
   *                    left click). A right click (or any click that opens the context menu) on a link
   *                    will be tracked as clicked even if "Open in new tab" is not selected.
   *                    * If "false" (default), nothing will be tracked on open context menu or middle click.
   *                    The context menu is usually opened to open a link / download in a new tab
   *                    therefore you can get more accurate results by treat it as a click but it can lead
   *                    to wrong click numbers.
   *
   * @noreturn
   */
  this.enableLinkTracking = function (enable) {
    if (linkTrackingEnabled) {
      return;
    }
    linkTrackingEnabled = true;

    if (!clickListenerInstalled) {
      clickListenerInstalled = true;
      h.trackCallbackOnReady(function () {
        const element = document.body;
        addClickListener(element, enable, true);
      });
    }
  };

  /**
   * Track button element clicks
   *
   * @param {boolean} enable
   *
   * @noreturn
   */
  this.enableButtonClickTracking = function (enable) {
    if (buttonClickTrackingEnabled) {
      return;
    }
    buttonClickTrackingEnabled = true;

    if (!clickListenerInstalled) {
      clickListenerInstalled = true;
      h.trackCallbackOnReady(function () {
        const element = document.body;
        addClickListener(element, enable, true);
      });
    }
  };

  /**
   * Track img element clicks
   */
  this.enableImageClickTracking = function (enable) {
    if (imageClickTrackingEnabled) {
      return;
    }
    imageClickTrackingEnabled = true;

    if (!clickListenerInstalled) {
      clickListenerInstalled = true;
      h.trackCallbackOnReady(function () {
        var element = globalThis.eave.documentAlias.body;
        addClickListener(element, enable, true);
      });
    }
  };

  /**
   * Tracks route-change history for single page applications, since
   * normal page view events aren't triggered for navigation without a GET request.
   *
   * @returns {string | undefined}
   */
  this.enableRouteHistoryTracking = function () {
    if (routeHistoryTrackingEnabled) {
      return;
    }
    routeHistoryTrackingEnabled = true;
    trackedContentImpressions = [];
    consentRequestsQueue = [];
    javaScriptErrors = [];

    function getCurrentUrl() {
      return window.location.href;
    }
    function getEventUrl(event) {
      if (
        event &&
        event.target &&
        event.target.location &&
        event.target.location.href
      ) {
        return event.target.location.href;
      }
      return getCurrentUrl();
    }
    function parseUrl(urlToParse, urlPart) {
      try {
        let loc = document.createElement("a");
        loc.href = urlToParse;
        const absUrl = loc.href;

        // needed to make tests work in IE10... we first need to convert URL to abs url
        loc = document.createElement("a");
        loc.href = absUrl;

        if (urlPart && urlPart in loc) {
          if ("hash" === urlPart) {
            return String(loc[urlPart]).replace("#", "");
          } else if ("protocol" === urlPart) {
            return String(loc[urlPart]).replace(":", "");
          } else if ("search" === urlPart) {
            return String(loc[urlPart]).replace("?", "");
          } else if ("port" === urlPart && !loc[urlPart]) {
            if (loc.protocol === "https:") {
              return "443";
            } else if (loc.protocol === "http:") {
              return "80";
            }
          }

          if (
            "pathname" === urlPart &&
            loc[urlPart] &&
            String(loc[urlPart]).substr(0, 1) !== "/"
          ) {
            return "/" + loc[urlPart]; // ie 10 doesn't return leading slash when not added to the dom
          }

          if ("port" === urlPart && loc[urlPart]) {
            return String(loc[urlPart]); // ie 10 returns int
          }

          return loc[urlPart];
        }

        if ("origin" === urlPart && "protocol" in loc && loc.protocol) {
          // fix for ie10
          return (
            loc.protocol +
            "//" +
            loc.hostname +
            (loc.port ? ":" + loc.port : "")
          );
        }
        return;
      } catch (e) {
        if ("function" === typeof URL) {
          const theUrl = new URL(urlToParse);
          if (urlPart && urlPart in theUrl) {
            if ("hash" === urlPart) {
              return String(theUrl[urlPart]).replace("#", "");
            } else if ("protocol" === urlPart) {
              return String(theUrl[urlPart]).replace(":", "");
            } else if ("search" === urlPart) {
              return String(theUrl[urlPart]).replace("?", "");
            } else if ("port" === urlPart && !theUrl[urlPart]) {
              if (theUrl.protocol === "https:") {
                return "443";
              } else if (theUrl.protocol === "http:") {
                return "80";
              }
            }
            return theUrl[urlPart];
          }
          return;
        }
      }
    }

    h.trackCallbackOnReady(function () {
      const initialUrl = getCurrentUrl();
      const origin = parseUrl(initialUrl, "origin");

      let lastEvent = {
        eventType: null,
        hash: parseUrl(initialUrl, "hash"),
        search: parseUrl(initialUrl, "search"),
        path: parseUrl(initialUrl, "pathname"),
      };

      function trigger(eventType, newUrl, newState) {
        const newEvent = {
          eventType: eventType,
          hash: parseUrl(newUrl, "hash"),
          search: parseUrl(newUrl, "search"),
          path: parseUrl(newUrl, "pathname"),
          state: newState,
        };

        let oldUrl = lastEvent.path;
        if (lastEvent.search) {
          oldUrl += "?" + lastEvent.search;
        }
        if (lastEvent.hash) {
          oldUrl += "#" + lastEvent.hash;
        }
        let nowUrl = newEvent.path;
        if (newEvent.search) {
          nowUrl += "?" + newEvent.search;
        }
        if (newEvent.hash) {
          nowUrl += "#" + newEvent.hash;
        }
        if (oldUrl !== nowUrl) {
          const tmpLast = lastEvent;
          lastEvent = newEvent; // overwrite as early as possible in case event gets triggered again

          trackCallback(function () {
            logPageView(
              "", // TODO: make more meaningful
              {
                event: "HistoryChange",
                historyChangeSource: newEvent.eventType,
                oldUrl: origin + oldUrl,
                newUrl: origin + nowUrl,
                oldUrlHash: tmpLast.hash,
                newUrlHash: newEvent.hash,
                oldUrlPath: tmpLast.path,
                newUrlPath: newEvent.path,
                oldUrlSearch: tmpLast.search,
                newUrlSearch: newEvent.search,
                oldHistoryState: tmpLast.state,
                newHistoryState: newEvent.state,
              },
            );
          });
        }
      }
      function setMethodWrapIfNeeded(
        contextObject,
        methodNameToReplace,
        callback,
      ) {
        if (!(methodNameToReplace in contextObject)) {
          contextObject[methodNameToReplace] = callback;
          return;
        }

        const oldMethodBackup = contextObject[methodNameToReplace];

        if (!h.isFunction(oldMethodBackup)) {
          contextObject[methodNameToReplace] = callback;
          return;
        }

        try {
          contextObject[methodNameToReplace] = function () {
            let value;
            try {
              value = oldMethodBackup.apply(
                contextObject,
                [].slice.call(arguments, 0),
              );
            } catch (e) {
              callback.apply(contextObject, [].slice.call(arguments, 0));
              throw e;
            }
            callback.apply(contextObject, [].slice.call(arguments, 0));
            return value;
          };
        } catch (ignore) {
          // ignore
        }
      }

      function replaceHistoryMethod(methodNameToReplace) {
        setMethodWrapIfNeeded(
          window.history,
          methodNameToReplace,
          function (state, _title, _urlParam) {
            trigger(methodNameToReplace, getCurrentUrl(), state);
          },
        );
      }

      replaceHistoryMethod("replaceState");
      replaceHistoryMethod("pushState");

      window.addEventListener(
        "hashchange",
        function (event) {
          const newUrl = getEventUrl(event);
          trigger("hashchange", newUrl, null);
        },
        false,
      );
      window.addEventListener(
        "popstate",
        function (event) {
          const newUrl = getEventUrl(event);
          trigger("popstate", newUrl, event.state);
        },
        false,
      );
    });
  };

  /**
   * Enable tracking of uncatched JavaScript errors
   *
   * If enabled, uncaught JavaScript Errors will be tracked as an event by defining a
   * window.onerror handler. If a window.onerror handler is already defined we will make
   * sure to call this previously registered error handler after tracking the error.
   *
   * By default we return false in the window.onerror handler to make sure the error still
   * appears in the browser's console etc. Note: Some older browsers might behave differently
   * so it could happen that an actual JavaScript error will be suppressed.
   * If a window.onerror handler was registered we will return the result of this handler.
   *
   * Make sure not to overwrite the window.onerror handler after enabling the JS error
   * tracking as the error tracking won't work otherwise. To capture all JS errors we
   * recommend to include the eave JavaScript tracker in the HTML as early as possible.
   * If possible directly in <head></head> before loading any other JavaScript.
   *
   * @noreturn
   */
  this.enableJSErrorTracking = function () {
    if (enableJSErrorTracking) {
      return;
    }

    enableJSErrorTracking = true;
    const onError = window.onerror;

    window.onerror = function (
      message,
      url,
      linenumber,
      column,
      error,
    ) {
      trackCallback(function () {
        const category = "JavaScript Errors";

        let action = url + ":" + linenumber;
        if (column) {
          action += ":" + column;
        }

        if (
          h.indexOfArray(javaScriptErrors, category + action + message) === -1
        ) {
          javaScriptErrors.push(category + action + message);

          let msg;
          if (typeof message === "string") {
            msg = message;
          } else {
            msg = message.type; // ?
          }

          logEvent(category, action, msg);

        }
      });

      if (onError) {
        return onError(message, url, linenumber, column, error);
      }

      return false;
    };
  };

  /**
   * Disable automatic performance tracking
   *
   * @noreturn
   */
  this.disablePerformanceTracking = function () {
    configPerformanceTrackingEnabled = false;
  };

  /**
   * Set heartbeat (in seconds)
   *
   * @param {number} heartBeatDelayInSeconds Defaults to 15s. Cannot be lower than 5.
   * @noreturn
   */
  this.enableHeartBeatTimer = function (heartBeatDelayInSeconds) {
    heartBeatDelayInSeconds = Math.max(heartBeatDelayInSeconds || 15, 5);
    configHeartBeatDelay = heartBeatDelayInSeconds * 1000;

    // if a tracking request has already been sent, start the heart beat timeout
    if (lastTrackerRequestTime !== null) {
      setUpHeartBeat();
    }
  };

  /**
   * Disable heartbeat if it was previously activated.
   *
   * @noreturn
   */
  this.disableHeartBeatTimer = function () {
    if (configHeartBeatDelay || heartBeatSetUp) {
      window.removeEventListener(
        "focus",
        heartBeatOnFocus,
      );
      window.removeEventListener(
        "blur",
        heartBeatOnBlur,
      );
      window.removeEventListener(
        "visibilitychange",
        heartBeatOnVisible,
      );
    }

    configHeartBeatDelay = null;
    heartBeatSetUp = false;
  };

  /**
   * Frame buster
   *
   * @noreturn
   */
  this.killFrame = function () {
    if (!window.top) {
      return;
    }

    if (window.location !== window.top.location) {
      window.top.location = window.location;
    }
  };

  /**
   * Redirect if browsing offline (aka file: buster)
   *
   * @param {string} url Redirect to this URL
   *
   * @noreturn
   */
  this.redirectFile = function (url) {
    if (window.location.protocol === "file:") {
      window.location = url;
    }
  };

  /**
   * Count sites in pre-rendered state
   *
   * @param {boolean} enable If true, track when in pre-rendered state
   * @noreturn
   */
  this.setCountPreRendered = function (enable) {
    configCountPreRendered = enable;
  };

  // /**
  //  * Trigger a goal
  //  *
  //  * @param {string} idGoal
  //  * @param {number} customRevenue
  //  * @param {object} customData
  //  * @param {() => void} callback
  //  * @noreturn
  //  */
  // this.trackGoal = function (idGoal, customRevenue, customData, callback) {
  //   trackCallback(function () {
  //     logGoal(idGoal, customRevenue, customData, callback);
  //   });
  // };

  /**
   * Manually log a click from your own code
   *
   * @param {string} sourceUrl
   * @param {string} linkType
   * @param {object} customData
   * @param {Types.RequestCallback | null} callback
   *
   * @noreturn
   */
  this.trackLink = function (sourceUrl, linkType, customData, callback) {
    trackCallback(function () {
      logLink(sourceUrl, linkType, customData, undefined, callback);
    });
  };

  /**
   * Get the number of page views that have been tracked so far within the currently loaded page.
   *
   * @returns {number}
   */
  this.getNumTrackedPageViews = function () {
    return numTrackedPageviews;
  };

  /**
   * Log visit to this page
   *
   * @param {string} customTitle
   * @param {object} customData
   * @param {() => void} callback
   *
   * @noreturn
   */
  this.trackPageView = function (customTitle, customData, callback) {
    trackedContentImpressions = [];
    consentRequestsQueue = [];
    javaScriptErrors = [];

    trackCallback(function () {
      numTrackedPageviews++;
      logPageView(customTitle, customData, callback);
    });
  };

  /**
   * @noreturn
   */
  this.disableBrowserFeatureDetection = function () {
    configBrowserFeatureDetection = false;
    browserFeatures = {};
    if (supportsClientHints()) {
      // ensure already queue requests are still processed
      processClientHintsQueue();
    }
  };

  /**
   * @noreturn
   */
  this.enableBrowserFeatureDetection = function () {
    configBrowserFeatureDetection = true;
    detectBrowserFeatures();
  };

  /**
   * Scans the entire DOM for all content blocks and tracks all impressions once the DOM ready event has
   * been triggered.
   *
   * If you only want to track visible content impressions have a look at `trackVisibleContentImpressions()`.
   * We do not track an impression of the same content block twice if you call this method multiple times
   * unless `trackPageView()` is called meanwhile. This is useful for single page applications.
   *
   * @noreturn
   */
  this.trackAllContentImpressions = function () {
    trackCallback(function () {
      h.trackCallbackOnReady(function () {
        // we have to wait till DOM ready
        const contentNodes = content.findContentNodes();
        const requests = getContentImpressionsRequestsFromNodes(contentNodes);

        requestQueue.pushMultiple(requests);
      });
    });
  };

  /**
   * Scans the entire DOM for all content blocks as soon as the page is loaded. It tracks an impression
   * only if a content block is actually visible. Meaning it is not hidden and the content is or was at
   * some point in the viewport.
   *
   * If you want to track all content blocks have a look at `trackAllContentImpressions()`.
   * We do not track an impression of the same content block twice if you call this method multiple times
   * unless `trackPageView()` is called meanwhile. This is useful for single page applications.
   *
   * Once you have called this method you can no longer change `checkOnScroll` or `timeIntervalInMs`.
   *
   * If you do want to only track visible content blocks but not want us to perform any automatic checks
   * as they can slow down your frames per second you can call `trackVisibleContentImpressions()` or
   * `trackContentImpressionsWithinNode()` manually at  any time to rescan the entire DOM for newly
   * visible content blocks.
   * o Call `trackVisibleContentImpressions(false, 0)` to initially track only visible content impressions
   * o Call `trackVisibleContentImpressions()` at any time again to rescan the entire DOM for newly visible content blocks or
   * o Call `trackContentImpressionsWithinNode(node)` at any time to rescan only a part of the DOM for newly visible content blocks
   *
   * @param {boolean} [checkOnScroll=true] Optional, you can disable rescanning the entire DOM automatically
   *                                     after each scroll event by passing the value `false`. If enabled,
   *                                     we check whether a previously hidden content blocks became visible
   *                                     after a scroll and if so track the impression.
   *                                     Note: If a content block is placed within a scrollable element
   *                                     (`overflow: scroll`), we can currently not detect when this block
   *                                     becomes visible.
   * @param {number} [timeIntervalInMs=750] Optional, you can define an interval to rescan the entire DOM
   *                                     for new impressions every X milliseconds by passing
   *                                     for instance `timeIntervalInMs=500` (rescan DOM every 500ms).
   *                                     Rescanning the entire DOM and detecting the visible state of content
   *                                     blocks can take a while depending on the browser and amount of content.
   *                                     In case your frames per second goes down you might want to increase
   *                                     this value or disable it by passing the value `0`.
   *
   * @noreturn
   */
  this.trackVisibleContentImpressions = function (
    checkOnScroll = true,
    timeIntervalInMs = 750,
  ) {

    enableTrackOnlyVisibleContent(checkOnScroll, timeIntervalInMs, this);

    trackCallback(function () {
      h.trackCallbackOnLoad(function () {
        // we have to wait till CSS parsed and applied
        const contentNodes = content.findContentNodes();
        const requests =
          getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
            contentNodes,
          );

        requestQueue.pushMultiple(requests);
      });
    });
  };

  /**
   * Tracks a content impression using the specified values. You should not call this method too often
   * as each call causes an XHR tracking request and can slow down your site or your server.
   *
   * @param {string} contentName  For instance "Ad Sale".
   * @param {string} [contentPiece='Unknown'] For instance a path to an image or the text of a text ad.
   * @param {string} [contentTarget] For instance the URL of a landing page.
   * @noreturn
   */
  this.trackContentImpression = function (
    contentName,
    contentPiece,
    contentTarget,
  ) {
    contentName = h.trim(contentName);
    contentPiece = h.trim(contentPiece);
    contentTarget = h.trim(contentTarget);

    if (!contentName) {
      return;
    }

    contentPiece = contentPiece || "Unknown";

    trackCallback(function () {
      const request = buildContentImpressionRequest(
        contentName,
        contentPiece,
        contentTarget,
      );
      requestQueue.push(request);
    });
  };

  /**
   * Scans the given DOM node and its children for content blocks and tracks an impression for them if
   * no impression was already tracked for it. If you have called `trackVisibleContentImpressions()`
   * upfront only visible content blocks will be tracked. You can use this method if you, for instance,
   * dynamically add an element using JavaScript to your DOM after we have tracked the initial impressions.
   *
   * @param {Element} domNode
   * @noreturn
   */
  this.trackContentImpressionsWithinNode = function (domNode) {
    trackCallback(function () {
      if (isTrackOnlyVisibleContentEnabled) {
        h.trackCallbackOnLoad(function () {
          // we have to wait till CSS parsed and applied
          const contentNodes = content.findContentNodesWithinNode(domNode);

          const requests =
            getCurrentlyVisibleContentImpressionsRequestsIfNotTrackedYet(
              contentNodes,
            );
          requestQueue.pushMultiple(requests);
        });
      } else {
        h.trackCallbackOnReady(function () {
          // we have to wait till DOM ready
          const contentNodes = content.findContentNodesWithinNode(domNode);

          const requests = getContentImpressionsRequestsFromNodes(contentNodes);
          requestQueue.pushMultiple(requests);
        });
      }
    });
  };

  /**
   * Tracks a content interaction using the specified values. You should use this method only in conjunction
   * with `trackContentImpression()`. The specified `contentName` and `contentPiece` has to be exactly the
   * same as the ones that were used in `trackContentImpression()`. Otherwise the interaction will not count.
   *
   * @param {string} contentInteraction The type of interaction that happened. For instance 'click' or 'submit'.
   * @param {string} contentName  The name of the content. For instance "Ad Sale".
   * @param {string} [contentPiece='Unknown'] The actual content. For instance a path to an image or the text of a text ad.
   * @param {string} [contentTarget] For instance the URL of a landing page.
   * @noreturn
   */
  this.trackContentInteraction = function (
    contentInteraction,
    contentName,
    contentPiece,
    contentTarget,
  ) {
    contentInteraction = h.trim(contentInteraction);
    contentName = h.trim(contentName);
    contentPiece = h.trim(contentPiece);
    contentTarget = h.trim(contentTarget);

    if (!contentInteraction || !contentName) {
      return;
    }

    contentPiece = contentPiece || "Unknown";

    trackCallback(function () {
      const request = buildContentInteractionRequest(
        contentInteraction,
        contentName,
        contentPiece,
        contentTarget,
      );
      if (request) {
        requestQueue.push(request);
      }
    });
  };

  /**
   * Tracks an interaction with the given DOM node / content block.
   *
   * By default we track interactions on click but sometimes you might want to track interactions yourself.
   * For instance you might want to track an interaction manually on a double click or a form submit.
   * Make sure to disable the automatic interaction tracking in this case by specifying either the CSS
   * class `eaveContentIgnoreInteraction` or the attribute `data-content-ignoreinteraction`.
   *
   * @param {EventTarget} domNode  This element itself or any of its parent elements has to be a content block
   *                         element. Meaning one of those has to have a `eaveTrackContent` CSS class or
   *                         a `data-track-content` attribute.
   * @param {string} [contentInteraction='Unknown] The name of the interaction that happened. For instance
   *                                             'click', 'formSubmit', 'DblClick', ...
   * @returns {string | null}
   */
  this.trackContentInteractionNode = function (domNode, contentInteraction) {
    let theRequest = null;

    trackCallback(function () {
      theRequest = buildContentInteractionRequestNode(
        domNode,
        contentInteraction,
      );
      if (theRequest) {
        requestQueue.push(theRequest);
      }
    });
    //note: return value is only for tests... will only work if dom is already ready...
    return theRequest;
  };

  /**
   * Useful to debug content tracking. This method will log all detected content blocks to console
   * (if the browser supports the console). It will list the detected name, piece, and target of each
   * content block.
   *
   * @noreturn
   */
  this.logAllContentBlocksOnPage = function () {
    const contentNodes = content.findContentNodes();
    const contents = content.collectContent(contentNodes);

    // needed to write it this way for jslint
    const consoleType = typeof console;
    if (consoleType !== "undefined" && console && console.log) {
      console.log(contents);
    }
  };

  /**
   * Records an event
   *
   * @param {string} category The Event Category (Videos, Music, Games...)
   * @param {string} action The Event's Action (Play, Pause, Duration, Add Playlist, Downloaded, Clicked...)
   * @param {string} [name] (optional) The Event's object Name (a particular Movie name, or Song name, or File name...)
   * @param {string} [value] (optional) The Event's value
   * @param {object} [customData]
   * @param {Types.RequestCallback | null} [callback]
   * @noreturn
   */
  this.trackEvent = function (
    category,
    action,
    name,
    value,
    customData,
    callback,
  ) {
    trackCallback(function () {
      logEvent(category, action, name, value, customData, callback);
    });
  };

  /**
   * Log special pageview: Internal search
   *
   * @param {string} keyword
   * @param {string} category
   * @param {number} resultsCount
   * @param {object} customData
   * @noreturn
   */
  this.trackSiteSearch = function (
    keyword,
    category,
    resultsCount,
    customData,
  ) {
    trackedContentImpressions = [];
    trackCallback(function () {
      logSiteSearch(keyword, category, resultsCount, customData);
    });
  };

  // /**
  //  * Used to record that the current page view is an item (product) page view, or a Ecommerce Category page view.
  //  * This must be called before trackPageView() on the product/category page.
  //  *
  //  * On a category page, you can set the parameter category, and set the other parameters to empty string or false
  //  *
  //  * Tracking Product/Category page views will allow eave to report on Product & Categories
  //  * conversion rates (Conversion rate = Ecommerce orders containing this product or category / Visits to the product or category)
  //  *
  //  * @param {string} sku Item's SKU code being viewed
  //  * @param {string} name Item's Name being viewed
  //  * @param {string} category Category page being viewed. On an Item's page, this is the item's category
  //  * @param {float} price Item's display price, not use in standard eave reports, but output in API product reports.
  //  */
  // this.setEcommerceView = function (sku, name, category, price) {
  //   ecommerceProductView = {};

  //   if (h.isNumberOrHasLength(category)) {
  //     category = String(category);
  //   }
  //   if (
  //     !h.isDefined(category) ||
  //     category === null ||
  //     category === false ||
  //     !category.length
  //   ) {
  //     category = "";
  //   } else if (category instanceof Array) {
  //     category = JSON.stringify(category);
  //   }

  //   let param = "_pkc";
  //   ecommerceProductView[param] = category;

  //   if (
  //     h.isDefined(price) &&
  //     price !== null &&
  //     price !== false &&
  //     String(price).length
  //   ) {
  //     param = "_pkp";
  //     ecommerceProductView[param] = price;
  //   }

  //   // On a category page, do not track Product name not defined
  //   if (!h.isNumberOrHasLength(sku) && !h.isNumberOrHasLength(name)) {
  //     return;
  //   }

  //   if (h.isNumberOrHasLength(sku)) {
  //     param = "_pks";
  //     ecommerceProductView[param] = sku;
  //   }

  //   if (!h.isNumberOrHasLength(name)) {
  //     name = "";
  //   }

  //   param = "_pkn";
  //   ecommerceProductView[param] = name;
  // };

  /**
   * Track form submission events
   *
   * @noreturn
   */
  this.enableFormTracking = function () {
    if (formTrackingEnabled) {
      return;
    }
    formTrackingEnabled = true;

    if (!formTrackerInstalled) {
      formTrackerInstalled = true;
      h.trackCallbackOnReady(function () {
        document.body.addEventListener(
          "submit",
          function (event) {
            if (!event.target) {
              return;
            }
            const target = event.target;
            if (target.nodeName === "FORM") {
              const formAction =
                target.getAttribute("action") ||
                window.location.href;

              logEvent(
                // TODO: details
                "form",
                "submit",
                "form submitted",
                formAction,
                {
                  // custom data
                  event: "FormSubmit",
                  formElement: target.outerHtml,
                  formElementId: target.getAttribute("id"),
                  formElementName: target.getAttribute("name"),
                  formElementClasses: target.className.split(" "),
                  formElementAction: formAction,
                },
                undefined, // callback
              );
            }
          },
          true,
        );
      });
    }
  };

  // /**
  //  * Returns the list of ecommerce items that will be sent when a cart update or order is tracked.
  //  * The returned value is read-only, modifications will not change what will be tracked. Use
  //  * addEcommerceItem/removeEcommerceItem/clearEcommerceCart to modify what items will be tracked.
  //  *
  //  * Note: the cart will be cleared after an order.
  //  *
  //  * @returns {Array}
  //  */
  // this.getEcommerceItems = function () {
  //   return JSON.parse(
  //     JSON.stringify(ecommerceItems),
  //   );
  // };

  // /**
  //  * Adds an item (product) that is in the current Cart or in the Ecommerce order.
  //  * This function is called for every item (product) in the Cart or the Order.
  //  * The only required parameter is sku.
  //  * The items are deleted from this JavaScript object when the Ecommerce order is tracked via the method trackEcommerceOrder.
  //  *
  //  * If there is already a saved item for the given sku, it will be updated with the
  //  * new information.
  //  *
  //  * @param {string} sku (required) Item's SKU Code. This is the unique identifier for the product.
  //  * @param {string} name (optional) Item's name
  //  * @param {string} category (optional) Item's category, or array of up to 5 categories
  //  * @param {float} price (optional) Item's price. If not specified, will default to 0
  //  * @param {float} quantity (optional) Item's quantity. If not specified, will default to 1
  //  */
  // this.addEcommerceItem = function (sku, name, category, price, quantity) {
  //   if (h.isNumberOrHasLength(sku)) {
  //     ecommerceItems[sku] = [String(sku), name, category, price, quantity];
  //   }
  // };

  // /**
  //  * Removes a single ecommerce item by SKU from the current cart.
  //  *
  //  * @param {string} sku (required) Item's SKU Code. This is the unique identifier for the product.
  //  */
  // this.removeEcommerceItem = function (sku) {
  //   if (h.isNumberOrHasLength(sku)) {
  //     sku = String(sku);
  //     delete ecommerceItems[sku];
  //   }
  // };

  // /**
  //  * Clears the current cart, removing all saved ecommerce items. Call this method to manually clear
  //  * the cart before sending an ecommerce order.
  //  */
  // this.clearEcommerceCart = function () {
  //   ecommerceItems = {};
  // };

  // /**
  //  * Tracks an Ecommerce order.
  //  * If the Ecommerce order contains items (products), you must call first the addEcommerceItem() for each item in the order.
  //  * All revenues (grandTotal, subTotal, tax, shipping, discount) will be individually summed and reported in eave reports.
  //  * Parameters orderId and grandTotal are required. For others, you can set to false if you don't need to specify them.
  //  * After calling this method, items added to the cart will be removed from this JavaScript object.
  //  *
  //  * @param {string|int} orderId (required) Unique Order ID.
  //  *                   This will be used to count this order only once in the event the order page is reloaded several times.
  //  *                   orderId must be unique for each transaction, even on different days, or the transaction will not be recorded by eave.
  //  * @param {float} grandTotal (required) Grand Total revenue of the transaction (including tax, shipping, etc.)
  //  * @param {float} subTotal (optional) Sub total amount, typically the sum of items prices for all items in this order (before Tax and Shipping costs are applied)
  //  * @param {float} tax (optional) Tax amount for this order
  //  * @param {float} shipping (optional) Shipping amount for this order
  //  * @param {float} discount (optional) Discounted amount in this order
  //  */
  // this.trackEcommerceOrder = function (
  //   orderId,
  //   grandTotal,
  //   subTotal,
  //   tax,
  //   shipping,
  //   discount,
  // ) {
  //   logEcommerceOrder(orderId, grandTotal, subTotal, tax, shipping, discount);
  // };

  // /**
  //  * Tracks a Cart Update (add item, remove item, update item).
  //  * On every Cart update, you must call addEcommerceItem() for each item (product) in the cart, including the items that haven't been updated since the last cart update.
  //  * Then you can call this function with the Cart grandTotal (typically the sum of all items' prices)
  //  * Calling this method does not remove from this JavaScript object the items that were added to the cart via addEcommerceItem
  //  *
  //  * @param {float} grandTotal (required) Items (products) amount in the Cart
  //  */
  // this.trackEcommerceCartUpdate = function (grandTotal) {
  //   logEcommerceCartUpdate(grandTotal);
  // };

  /**
   * Sends a tracking request with custom request parameters.
   * eave will prepend the hostname and path to eave, as well as all other needed tracking request
   * parameters prior to sending the request. Useful eg if you track custom dimensions via a plugin.
   *
   * @param {string} request eg. "param=value&param2=value2"
   * @param {object} customData
   * @param {string} pluginMethod
   * @param {Types.RequestCallback | null} [callback]
   *
   * @noreturn
   */
  this.trackRequest = function (request, customData, pluginMethod, callback) {
    trackCallback(function () {
      const fullRequest = getRequest(request, customData, pluginMethod);
      sendRequest(fullRequest, configTrackerPause, callback);
    });
  };

  /**
   * Sends a ping request.
   *
   * Ping requests do not track new actions. If they are sent within the standard visit length, they will
   * extend the existing visit and the current last action for the visit. If after the standard visit
   * length, ping requests will create a new visit using the last action in the last known visit.
   *
   * @noreturn
   */
  this.ping = function () {
    this.trackRequest("ping=1", null, "ping");
  };

  /**
   * Disables sending requests queued
   *
   * @noreturn
   */
  this.disableQueueRequest = function () {
    requestQueue.enabled = false;
  };

  /**
   * Defines after how many ms a queued requests will be executed after the request was queued initially.
   * The higher the value the more tracking requests can be send together at once.
   *
   * @throws {Error}
   *
   * @noreturn
   */
  this.setRequestQueueInterval = function (interval) {
    if (interval < 1000) {
      throw new Error("Request queue interval needs to be at least 1000ms");
    }
    requestQueue.interval = interval;
  };

  /**
   * Won't send the tracking request directly but wait for a short time to possibly send this tracking request
   * along with other tracking requests in one go. This can reduce the number of requests send to your server.
   * If the page unloads (user navigates to another page or closes the browser), then all remaining queued
   * requests will be sent immediately so that no tracking request gets lost.
   * Note: Any queued request may not be possible to be replayed in case a POST request is sent. Only queue
   * requests that don't have to be replayed.
   *
   * @param {string} request eg. "param=value&param2=value2"
   * @param {boolean} isFullRequest whether request is a full tracking request or not. If true, we don't call
   *                      call getRequest() before pushing to the queue.
   *
   * @noreturn
   */
  this.queueRequest = function (request, isFullRequest) {
    trackCallback(function () {
      const fullRequest = isFullRequest ? request : getRequest(request);
      requestQueue.push(fullRequest);
    });
  };

  /**
   * Returns whether consent is required or not.
   *
   * @returns {boolean}
   */
  this.isConsentRequired = function () {
    return configConsentRequired;
  };

  /**
   * If the user has given consent previously and this consent was remembered, it will return the number
   * in milliseconds since 1970/01/01 which is the date when the user has given consent. Please note that
   * the returned time depends on the users local time which may not always be correct.
   *
   * @returns {number | string | null}
   */
  this.getRememberedConsent = function () {
    const value = cookieManager.getCookie(cookieManager.CONSENT_COOKIE_NAME);
    if (cookieManager.getCookie(cookieManager.CONSENT_REMOVED_COOKIE_NAME)) {
      // if for some reason the consent_removed cookie is also set with the consent cookie, the
      // consent_removed cookie overrides the consent one, and we make sure to delete the consent
      // cookie.
      if (value) {
        cookieManager.deleteCookie(
          cookieManager.CONSENT_COOKIE_NAME,
          cookieManager.configCookiePath,
          cookieManager.configCookieDomain,
        );
      }
      return null;
    }

    if (!value) {
      return null;
    }
    return value;
  };

  /**
   * Detects whether the user has given consent previously.
   *
   * @returns {boolean}
   */
  this.hasRememberedConsent = function () {
    return !!this.getRememberedConsent();
  };

  /**
   * When called, no tracking request will be sent to the eave server until you have called `setConsentGiven()`
   * unless consent was given previously AND you called {@link rememberConsentGiven()} when the user gave their
   * consent.
   *
   * This may be useful when you want to implement for example a popup to ask for consent before tracking the user.
   * Once the user has given consent, you should call {@link setConsentGiven()} or {@link rememberConsentGiven()}.
   *
   * If you require consent for tracking personal data for example, you should first call
   * `settings.push(['requireConsent'])`.
   *
   * If the user has already given consent in the past, you can either decide to not call `requireConsent` at all
   * or call `settings.push(['setConsentGiven'])` on each page view at any time after calling `requireConsent`.
   *
   * When the user gives you the consent to track data, you can also call `settings.push(['rememberConsentGiven', optionalTimeoutInHours])`
   * and for the duration while the consent is remembered, any call to `requireConsent` will be automatically ignored until you call `forgetConsentGiven`.
   * `forgetConsentGiven` needs to be called when the user removes consent for tracking. This means if you call `rememberConsentGiven` at the
   * time the user gives you consent, you do not need to ever call `settings.push(['setConsentGiven'])`.
   *
   * @noreturn
   */
  this.requireConsent = function () {
    configConsentRequired = true;
    configHasConsent = this.hasRememberedConsent();
    if (!configHasConsent) {
      // we won't call this.disableCookies() since we don't want to delete any cookies just yet
      // user might call `setConsentGiven` next
      cookieManager.configCookiesDisabled = true;
    }
    // eave.addPlugin might not be defined at this point, we add the plugin directly also to make JSLint happy
    // We also want to make sure to define an unload listener for each tracker, not only one tracker.
    eaveWindow.eave.coreConsentCounter++;
    eaveWindow.eave.plugins[
      "CoreConsent" + eaveWindow.eave.coreConsentCounter
    ] = {
      unload: function () {
        if (!configHasConsent) {
          // we want to make sure to remove all previously set cookies again
          cookieManager.deleteEaveCookies();
        }
      },
    };
  };

  /**
   * Call this method once the user has given consent. This will cause all tracking requests from this
   * page view to be sent. Please note that the given consent won't be remembered across page views. If you
   * want to remember consent across page views, call {@link rememberConsentGiven()} instead.
   *
   * It will also automatically enable cookies if they were disabled previously.
   *
   * @param {boolean} [setCookieConsent=true] Internal parameter. Defines whether cookies should be enabled or not.
   * @noreturn
   */
  this.setConsentGiven = function (setCookieConsent) {
    configHasConsent = true;
    if (!configBrowserFeatureDetection) {
      this.enableBrowserFeatureDetection();
    }
    if (!configEnableCampaignParameters) {
      this.enableCampaignParameters();
    }

    cookieManager.deleteCookie(
      cookieManager.CONSENT_REMOVED_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );

    var i, requestType;
    for (i = 0; i < consentRequestsQueue.length; i++) {
      requestType = typeof consentRequestsQueue[i][0];
      if (requestType === "string") {
        sendRequest(
          consentRequestsQueue[i][0],
          configTrackerPause,
          consentRequestsQueue[i][1],
        );
      } else if (requestType === "object") {
        sendBulkRequest(consentRequestsQueue[i][0], configTrackerPause);
      }
    }
    consentRequestsQueue = [];

    // we need to enable cookies after sending the previous requests as it will make sure that we send
    // a ping request if needed. Cookies are only set once we call `getRequest`. Above only calls sendRequest
    // meaning no cookies will be created unless we called enableCookies after at least one request has been sent.
    // this will cause a ping request to be sent that sets the cookies and also updates the newly generated visitorId
    // on the server.
    // If the user calls setConsentGiven before sending any tracking request (which usually is the case) then
    // nothing will need to be done as it only enables cookies and the next tracking request will set the cookies
    // etc.
    if (!h.isDefined(setCookieConsent) || setCookieConsent) {
      this.setCookieConsentGiven();
    }
  };

  /**
   * Calling this method will remember that the user has given consent across multiple requests by setting
   * a cookie. You can optionally define the lifetime of that cookie in hours using a parameter.
   *
   * When you call this method, we imply that the user has given consent for this page view, and will also
   * imply consent for all future page views unless the cookie expires (if timeout defined) or the user
   * deletes all their cookies. This means even if you call {@link requireConsent()}, then all requests
   * will still be tracked.
   *
   * Please note that this feature requires you to set the `cookieDomain` and `cookiePath` correctly and requires
   * that you do not disable cookies. Please also note that when you call this method, consent will be implied
   * for all sites that match the configured cookieDomain and cookiePath. Depending on your website structure,
   * you may need to restrict or widen the scope of the cookie domain/path to ensure the consent is applied
   * to the sites you want.
   *
   * @param {number} hoursToExpire After how many hours the consent should expire. By default the consent is valid
   *                          for 30 years unless cookies are deleted by the user or the browser prior to this
   *
   * @noreturn
   */
  this.rememberConsentGiven = function (hoursToExpire) {
    if (hoursToExpire) {
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }
    const setCookieConsent = true;
    // we currently always enable cookies if we remember consent cause we don't store across requests whether
    // cookies should be automatically enabled or not.
    this.setConsentGiven(setCookieConsent);
    const now = new Date().getTime();
    cookieManager.setCookie(
      cookieManager.CONSENT_COOKIE_NAME,
      String(now),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
  };

  /**
   * Calling this method will remove any previously given consent and during this page view no request
   * will be sent anymore ({@link requireConsent()}) will be called automatically to ensure the removed
   * consent will be enforced. You may call this method if the user removes consent manually, or if you
   * want to re-ask for consent after a specific time period. You can optionally define the lifetime of
   * the CONSENT_REMOVED_COOKIE_NAME cookie in hours using a parameter.
   *
   * @param {number} hoursToExpire  After how many hours the CONSENT_REMOVED_COOKIE_NAME cookie should expire.
   *                                By default the consent is valid for 30 years unless cookies are deleted by the user or the browser
   *                                prior to this
   * @noreturn
   */
  this.forgetConsentGiven = function (hoursToExpire) {
    if (hoursToExpire) {
      hoursToExpire = hoursToExpire * 60 * 60 * 1000;
    } else {
      hoursToExpire = 30 * 365 * 24 * 60 * 60 * 1000;
    }

    cookieManager.deleteCookie(
      cookieManager.CONSENT_COOKIE_NAME,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
    );
    cookieManager.setCookie(
      cookieManager.CONSENT_REMOVED_COOKIE_NAME,
      String(new Date().getTime()),
      hoursToExpire,
      cookieManager.configCookiePath,
      cookieManager.configCookieDomain,
      cookieManager.configCookieIsSecure,
      cookieManager.configCookieSameSite,
    );
    this.forgetCookieConsentGiven();
    this.requireConsent();
  };

  /**
   * Returns true if user is opted out, false if otherwise.
   *
   * @returns {boolean}
   */
  this.isUserOptedOut = function () {
    return !configHasConsent;
  };

  /**
   * Alias for forgetConsentGiven(). After calling this function, the user will no longer be tracked,
   * (even if they come back to the site).
   *
   * @type {(hoursToExpire: number) => void}
   */
  this.optUserOut = this.forgetConsentGiven;

  /**
   * Alias for rememberConsentGiven(). After calling this function, the current user will be tracked.
   *
   * @noreturn
   */
  this.forgetUserOptOut = function () {
    // we can't automatically enable cookies here as we don't know if user actually gave consent for cookies
    this.setConsentGiven(false);
  };

  /**
   * enable protocol file: format tracking
   *
   * @noreturn
   */
  this.enableFileTracking = function () {
    configFileTracking = true;
  };

  /**
   * Set initial eave tracking cookies as necessary.
   *
   * @noreturn
   */
  function setTrackingCookies() {
    // (session_id is reset on every pageView event, which will trigger directly after this)
    // set visitor_id if needed
    cookieManager.setVisitorId();

    // set referral data, if any
    maybeSetReferrerAttribution();
  }

  /** @type {() => void} */
  this.setTrackingCookies = setTrackingCookies;

  /**
   * Mark performance metrics as available, once onload event has finished
   */
  h.trackCallbackOnLoad(function () {
    setTimeout(function () {
      performanceAvailable = true;
    }, 0);
  });

  eaveWindow.eave.tracker.trigger("TrackerSetup", [this]);

  eaveWindow.eave.eave?.addPlugin("TrackerVisitorIdCookie" + uniqueTrackerId, {
    // if no tracking request was sent we refresh the visitor id cookie on page unload
    unload: function () {
      if (supportsClientHints() && !clientHintsResolved) {
        clientHintsResolved = true;
        processClientHintsQueue(); // ensure possible queued request are sent out
      }

      if (!hasSentTrackingRequestYet) {
        setTrackingCookies();
      }
    },
  });
}
