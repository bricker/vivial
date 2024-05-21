// @ts-check

import content from "./content.mjs";
import { CookieManager } from "./cookies.mjs";
import "./main.mjs";
import * as h from "./helpers.mjs";
import query from "./query.mjs";
import { isVisible } from "./visibility.mjs";
// eslint-disable-next-line no-unused-vars
import * as Types from "./types.mjs";

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

  /*<DEBUG>*/
  /*
    * registered test hooks
    */
  const registeredHooks = {};
  /*</DEBUG>*/

  // constants
  const trackerInstance = this;
  // Current URL and Referrer URL
  const [currentHostnameResolved, currentHrefResolved, currentReferrerResolved] = h.urlFixup(
    window.location.href,
    h.getReferrer(),
  );
  const domainAlias = h.domainFixup(currentHostnameResolved);
  const configReferrerUrl = currentReferrerResolved;
  let enableJSErrorTracking = false;
  const defaultRequestMethod = "GET";
  // Request method (GET or POST)
  let configRequestMethod = defaultRequestMethod;
  const defaultRequestContentType = "application/x-www-form-urlencoded; charset=UTF-8";
  // Request Content-Type header value; applicable when POST request method is used for submitting tracking events
  const configRequestContentType = defaultRequestContentType;
  // Tracker URL
  let configTrackerUrl = trackerUrl || "";
  // This string is appended to the Tracker URL Request (eg. to send data that is not handled by the existing setters/getters)
  let configAppendToTrackingUrl = "";
  // setPagePerformanceTiming sets this manually for SPAs
  let customPagePerformanceTiming = "";
  // Site ID
  const configTrackerSiteId = siteId || "";
  // Document title
  let configTitle = "";
  // Extensions to be treated as download links
  let configDownloadExtensions = [
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
  ];
  // Hosts or alias(es) to not treat as outlinks
  let configHostsAlias = [domainAlias];
  // HTML anchor element classes to not track
  let configIgnoreClasses = [];
  // Referrer URLs that should be excluded
  let configExcludedReferrers = [".paypal.com"];
  // Query parameters to be excluded
  let configExcludedQueryParams = [];
  // HTML anchor element classes to treat as downloads
  let configDownloadClasses = [];
  // Maximum delay to wait for web bug image to be fetched (in milliseconds)
  let configTrackerPause = 500;
  // If enabled, always use sendBeacon if the browser supports it
  let configAlwaysUseSendBeacon = true;
  // Recurring heart beat after initial ping (in milliseconds)
  let configHeartBeatDelay;
  // alias to circumvent circular function dependency (JSLint requires this)
  let heartBeatPingIfActivityAlias;
  // Disallow hash tags in URL
  let configDiscardHashTag;
  // Custom data
  let configCustomData;
  // the URL parameter that will store the visitorId if cross domain linking is enabled
  // ev_vid = visitor ID
  // first part of this URL parameter will be 16 char visitor Id.
  // The second part is the 10 char current timestamp and the third and last part will be a 6 characters deviceId
  // timestamp is needed to prevent reusing the visitorId when the URL is shared. The visitorId will be
  // only reused if the timestamp is less than 45 seconds old.
  // deviceId parameter is needed to prevent reusing the visitorId when the URL is shared. The visitorId
  // will be only reused if the device is still the same when opening the link.
  // VDI = visitor device identifier
  const configVisitorIdUrlParameter = "ev_vid";
  const configReferralQueryParamsKey = "referrer_query_params";
  const configReferralTimestampKey = "referrer_timestamp";
  const configReferralUrlKey = "referrer_url";
  // Is performance tracking enabled
  let configPerformanceTrackingEnabled = true;
  // will be set to true automatically once the onload event has finished
  let performanceAvailable = false;
  // indicates if performance metrics for the page view have been sent with a request
  let performanceTracked = false;
  // Whether Custom Variables scope "visit" should be stored in a cookie during the time of the visit
  let configStoreCustomVariablesInCookie = false;
  // Custom Variables read from cookie, scope "visit"
  let customVariables = false;
  let configCustomRequestContentProcessing;
  // Do Not Track
  let configDoNotTrack;
  // Count sites which are pre-rendered
  let configCountPreRendered;
  // Enable sending campaign parameters to backend.
  let configEnableCampaignParameters = true;
  // Custom Variables, scope "page"
  let customVariablesPage = {};
  // Custom Variables, scope "event"
  let customVariablesEvent = {};
  // Custom Dimensions (can be any scope)
  const customDimensions = {};
  // Custom Variables names and values are each truncated before being sent in the request or recorded in the cookie
  const customVariableMaximumLength = 200;
  // // Ecommerce product view
  // ecommerceProductView = {},
  // // Ecommerce items
  // ecommerceItems = {},

  /**
   * Browser features via client-side data collection
   *
   * @type {{[key:string]: string}}
   */
  let browserFeatures = {};

  /**
   * Browser client hints
   *
   * @type {{[key:string]: string}}
   */
  let clientHints = {};

  /**
   * @type {Types.RequestPayload[]}
   */
  let clientHintsRequestQueue = [];

  /**
   * holds all pending tracking requests that have not been tracked because we need consent
   *
   * @type {Types.RequestPayload[]}
   */
  let consentRequestsQueue = [];

  let clientHintsResolved = false;
  let clientHintsResolving = false;
  // Keeps track of previously tracked content impressions
  let trackedContentImpressions = [];
  let isTrackOnlyVisibleContentEnabled = false;
  // Guard to prevent empty visits see #6415. If there is a new visitor and the first 2 (or 3 or 4)
  // tracking requests are at nearly same time (eg trackPageView and trackContentImpression) 2 or more
  // visits will be created
  let timeNextTrackingRequestCanBeExecutedImmediately = -1;
  // Guard against installing the link tracker more than once per Tracker instance
  let clickListenerInstalled = false;
  let linkTrackingEnabled = false;
  let imageClickTrackingEnabled = false;
  let crossDomainTrackingEnabled = false;
  // Guard against installing route history tracker more than once per instance
  let routeHistoryTrackingEnabled = false;
  // Guard against installing button click tracker more than once per instance
  let buttonClickTrackingEnabled = false;
  // Guard against double installing form tracking
  let formTrackingEnabled = false;
  let formTrackerInstalled = false;
  // Guard against installing the activity tracker more than once per Tracker instance
  let heartBeatSetUp = false;
  let hadWindowFocusAtLeastOnce = false;
  let timeWindowLastFocused = null;
  // Timestamp of last tracker request sent to eave
  let lastTrackerRequestTime = null;
  // Internal state of the pseudo click handler
  let lastButton;
  let lastTarget;
  let configIdPageView;
  // Boolean indicating that a page view ID has been set manually
  let configIdPageViewSetManually = false;
  // we measure how many pageviews have been tracked so plugins can use it to eg detect if a
  // pageview was already tracked or not
  let numTrackedPageviews = 0;
  // whether requireConsent() was called or not
  let configConsentRequired = false;
  // we always have the concept of consent. by default consent is assumed unless the end user removes it,
  // or unless a eave user explicitly requires consent (via requireConsent())
  let configHasConsent = null; // initialized below

  // holds the actual javascript errors if enableJSErrorTracking is on, if the very same error is
  // happening multiple times, then it will be tracked only once within the same page view
  let javaScriptErrors = [];
  // a unique ID for this tracker during this request
  const uniqueTrackerId = eaveWindow.eave.trackerIdCounter++;
  // whether a tracking request has been sent yet during this page view
  let hasSentTrackingRequestYet = false;
  let configBrowserFeatureDetection = true;
  const cookieManager = new CookieManager();
  let configFileTracking = false;
  let eaveClientId = null;

  configTitle = document.title;

  configHasConsent = !cookieManager.getCookie(
    cookieManager.CONSENT_REMOVED_COOKIE_NAME,
  );



  /**
   * @noreturn
   */
  function processClientHintsQueue() {
    sendRequest(clientHintsRequestQueue);
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

    browserFeatures.cookie = navigator.cookieEnabled
      ? "1"
      : "0";

    const width = screen.width;
    const height = screen.height;
    browserFeatures.res = `${width}x${height}`;
    return browserFeatures;
  }

  /**
   * Modifies the input to add browser feature and client hint attributes.
   *
   * @param {Types.RequestPayload} payload
   *
   * @noreturn
   */
  function injectBrowserFeaturesAndClientHints(payload) {
    payload.browserFeatures = browserFeatures;
    payload.uadata = clientHints;
    return payload;
  }

  function supportsClientHints() {
    // [bcr] Not widely supported - https://developer.mozilla.org/en-US/docs/Web/API/Navigator/userAgentData
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
   * Is the host local? (i.e., not an outlink)
   *
   * @param {string} hostName
   *
   * @returns {boolean}
   */
  function isSiteHostName(hostName) {
    let alias;
    let offset;

    for (let i = 0; i < configHostsAlias.length; i++) {
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
    let aliasHost;
    let aliasPath;

    for (let i = 0; i < configHostsAlias.length; i++) {
      aliasHost = h.domainFixup(configHostsAlias[i]);
      aliasPath = getPathName(configHostsAlias[i]);

      if (h.isSameHost(host, aliasHost) && h.isSitePath(path, aliasPath)) {
        return true;
      }
    }

    return false;
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
   * @param {Element} anyNode
   * @param {any} interaction
   * @param {any} fallbackTarget
   *
   * @returns {string | undefined}
   */
  this.appendContentInteractionToRequestIfPossible = getContentInteractionToRequestIfPossible;

  /**
   * @param {HTMLElement} node
   *
   * @returns {boolean}
   */
  this.internalIsNodeVisible = isVisible;

  /**
   * @returns {string[]}
   */
  this.getDomains = function () {
    return configHostsAlias;
  };


  /**
   * @returns {string}
   */
  this.getConfigIdPageView = function () {
    return configIdPageView;
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
   * Disable automatic performance tracking
   *
   * @noreturn
   */
  this.disablePerformanceTracking = function () {
    configPerformanceTrackingEnabled = false;
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

  // [bcr] we don't use the goals feature
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
