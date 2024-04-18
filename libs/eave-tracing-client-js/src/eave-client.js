/*!
 * Eave - Intelligent Analytics
 *
 * JavaScript tracking client
 *
 * @link https://eave.fyi
 * @source https://github.com/eave-fyi/eave-tracing-client-js/
 * @license https://www.gnu.org/licenses/gpl-3.0.en.html#license-text GPLv3 (also in LICENSE.txt)
 */

/*
modified from 
 * https://github.com/matomo-org/tag-manager/ (GPLv3)
 * https://github.com/matomo-org/matomo/js/piwik.js (BSD-3)
*/

/*
 * Browser [In]Compatibility
 * - minimum required ECMAScript: ECMA-262, edition 3
 *
 * Incompatible with these (and earlier) versions of:
 * - IE4 - try..catch and for..in introduced in IE5
 * - IE5 - named anonymous functions, array.push, encodeURIComponent, decodeURIComponent, and getElementsByTagName introduced in IE5.5
 * - IE6 and 7 - window.JSON introduced in IE8
 * - Firefox 1.0 and Netscape 8.x - FF1.5 adds array.indexOf, among other things
 * - Mozilla 1.7 and Netscape 6.x-7.x
 * - Netscape 4.8
 * - Opera 6 - Error object (and Presto) introduced in Opera 7
 * - Opera 7
 */

import content from "./content.js";
import "./globals.js";
import * as h from "./helpers.js";
import { Tracker } from "./tracker.js";
import { isVisible } from "./visibility.js";

// eave singleton and namespace
if (typeof window.eave !== "object") {
  window.eave = (function () {
    "use strict";

    function TrackerProxy() {
      return {
        push: h.apply,
      };
    }

    /**
     * Applies the given methods in the given order if they are present in paq.
     *
     * @param {Array} paq
     * @param {Array} methodsToApply an array containing method names in the order that they should be applied
     *                 eg ['setSiteId', 'setTrackerUrl']
     * @returns {Array} the modified paq array with the methods that were already applied set to undefined
     */
    function applyMethodsInOrder(paq, methodsToApply) {
      var appliedMethods = {};
      var index, iterator;

      for (index = 0; index < methodsToApply.length; index++) {
        var methodNameToApply = methodsToApply[index];
        appliedMethods[methodNameToApply] = 1;

        for (iterator = 0; iterator < paq.length; iterator++) {
          if (paq[iterator] && paq[iterator][0]) {
            var methodName = paq[iterator][0];

            if (methodNameToApply === methodName) {
              h.apply(paq[iterator]);
              delete paq[iterator];

              if (
                appliedMethods[methodName] > 1 &&
                methodName !== "addTracker" &&
                methodName !== "enableLinkTracking"
              ) {
                h.logConsoleError(
                  "The method " +
                    methodName +
                    ' is registered more than once in "global.eave._paq" variable. Only the last call has an effect. Please have a look at the multiple eave trackers documentation: https://developer.matomo.org/guides/tracking-javascript-guide#multiple-piwik-trackers',
                );
              }

              appliedMethods[methodName]++;
            }
          }
        }
      }

      return paq;
    }

    /************************************************************
     * Constructor
     ************************************************************/

    var applyFirst = [
      "addTracker",
      "enableFileTracking",
      "forgetCookieConsentGiven",
      "requireCookieConsent",
      "disableBrowserFeatureDetection",
      "disableCampaignParameters",
      "disableCookies",
      "setTrackerUrl",
      "setAPIUrl",
      "enableCrossDomainLinking",
      "setCrossDomainLinkingTimeout",
      "setSessionCookieTimeout",
      "setVisitorCookieTimeout",
      "setCookieNamePrefix",
      "setCookieSameSite",
      "setSecureCookie",
      "setCookiePath",
      "setCookieDomain",
      "setDomains",
      "setUserId",
      "setVisitorId",
      "setSiteId",
      "alwaysUseSendBeacon",
      "disableAlwaysUseSendBeacon",
      "enableLinkTracking",
      "setCookieConsentGiven",
      "requireConsent",
      "setConsentGiven",
      "disablePerformanceTracking",
      "setPagePerformanceTiming",
      "setExcludedQueryParams",
      "setExcludedReferrers",
    ];

    function createFirstTracker(eaveUrl, siteId) {
      var tracker = new Tracker(eaveUrl, siteId);
      global.eave.asyncTrackers.push(tracker);

      global.eave._paq = applyMethodsInOrder(global.eave._paq, applyFirst);

      // apply the queue of actions
      for (var iterator = 0; iterator < global.eave._paq.length; iterator++) {
        if (global.eave._paq[iterator]) {
          h.apply(global.eave._paq[iterator]);
        }
      }

      // replace initialization array with proxy object
      global.eave._paq = new TrackerProxy();

      global.eave.eave.trigger("TrackerAdded", [tracker]);

      return tracker;
    }

    /************************************************************
     * Proxy object
     * - this allows the caller to continue push()'ing to global.eave._paq
     *   after the Tracker has been initialized and loaded
     ************************************************************/

    // initialize the eave singleton
    h.addEventListener(
      global.eave.windowAlias,
      "beforeunload",
      h.beforeUnloadHandler,
      false,
    );
    h.addEventListener(
      global.eave.windowAlias,
      "visibilitychange",
      function () {
        // if unloaded, return
        if (global.eave.isPageUnloading) {
          return;
        }
        // if not visible
        if (global.eave.documentAlias.visibilityState === "hidden") {
          h.executePluginMethod("unload");
        }
      },
      false,
    );
    h.addEventListener(
      global.eave.windowAlias,
      "online",
      function () {
        if (h.isDefined(global.eave.navigatorAlias.serviceWorker)) {
          global.eave.navigatorAlias.serviceWorker.ready.then(
            function (swRegistration) {
              if (swRegistration && swRegistration.sync) {
                return swRegistration.sync.register("eaveSync");
              }
            },
            function () {
              // handle (but ignore) failed promise, see https://github.com/matomo-org/matomo/issues/17454
            },
          );
        }
      },
      false,
    );

    h.addEventListener(
      global.eave.windowAlias,
      "message",
      function (e) {
        if (!e || !e.origin) {
          return;
        }

        var tracker, i, eaveHost;
        var originHost = h.getHostName(e.origin);

        var trackers = global.eave.eave.getAsyncTrackers();
        for (i = 0; i < trackers.length; i++) {
          eaveHost = h.getHostName(trackers[i].getEaveUrl());

          // find the matching tracker
          if (eaveHost === originHost) {
            tracker = trackers[i];
            break;
          }
        }

        if (!tracker) {
          // no matching tracker
          // Don't accept the message unless it came from the expected origin
          return;
        }

        var data = null;
        try {
          data = JSON.parse(e.data);
        } catch (ex) {
          return;
        }

        if (!data) {
          return;
        }

        function postMessageToCorrectFrame(postMessage) {
          // Find the iframe with the right URL to send it back to
          var iframes = global.eave.documentAlias.getElementsByTagName("iframe");
          for (i = 0; i < iframes.length; i++) {
            var iframe = iframes[i];
            var iframeHost = h.getHostName(iframe.src);

            if (
              iframe.contentWindow &&
              h.isDefined(iframe.contentWindow.postMessage) &&
              iframeHost === originHost
            ) {
              var jsonMessage = JSON.stringify(postMessage);
              iframe.contentWindow.postMessage(jsonMessage, e.origin);
            }
          }
        }

        // This listener can process two kinds of messages
        // 1) maq_initial_value => sent by optout iframe when it finishes loading.  Passes the value of the third
        // party opt-out cookie (if set) - we need to use this and any first-party cookies that are present to
        // initialise the configHasConsent value and send back the result so that the display can be updated.
        // 2) maq_opted_in => sent by optout iframe when the user changes their optout setting.  We need to update
        // our first-party cookie.
        if (h.isDefined(data.maq_initial_value)) {
          // Make a message to tell the optout iframe about the current state

          postMessageToCorrectFrame({
            maq_opted_in: data.maq_initial_value && tracker.hasConsent(),
            maq_url: tracker.getEaveUrl(),
            maq_optout_by_default: tracker.isConsentRequired(),
          });
        } else if (h.isDefined(data.maq_opted_in)) {
          // perform the opt in or opt out...
          trackers = global.eave.eave.getAsyncTrackers();
          for (i = 0; i < trackers.length; i++) {
            tracker = trackers[i];
            if (data.maq_opted_in) {
              tracker.rememberConsentGiven();
            } else {
              tracker.forgetConsentGiven();
            }
          }

          // Make a message to tell the optout iframe about the current state
          postMessageToCorrectFrame({
            maq_confirm_opted_in: tracker.hasConsent(),
            maq_url: tracker.getEaveUrl(),
            maq_optout_by_default: tracker.isConsentRequired(),
          });
        }
      },
      false,
    );

    Date.prototype.getTimeAlias = Date.prototype.getTime;

    /************************************************************
     * Public data and methods
     ************************************************************/

    global.eave.eave = {
      initialized: false,

      JSON: global.eave.windowAlias.JSON,

      /**
       * DOM Document related methods
       */
      DOM: {
        /**
         * Adds an event listener to the given element.
         * @param element
         * @param eventType
         * @param eventHandler
         * @param useCapture  Optional
         */
        addEventListener: function (
          element,
          eventType,
          eventHandler,
          useCapture,
        ) {
          var captureType = typeof useCapture;
          if (captureType === "undefined") {
            useCapture = false;
          }

          h.addEventListener(element, eventType, eventHandler, useCapture);
        },
        /**
         * Specify a function to execute when the DOM is fully loaded.
         *
         * If the DOM is already loaded, the function will be executed immediately.
         *
         * @param {Function} callback
         */
        onLoad: h.trackCallbackOnLoad,

        /**
         * Specify a function to execute when the DOM is ready.
         *
         * If the DOM is already ready, the function will be executed immediately.
         *
         * @param {Function} callback
         */
        onReady: h.trackCallbackOnReady,

        /**
         * Detect whether a node is visible right now.
         */
        isNodeVisible: isVisible,

        /**
         * Detect whether a node has been visible at some point
         */
        isOrWasNodeVisible: content.isNodeVisible,
      },

      /**
       * Listen to an event and invoke the handler when a the event is triggered.
       *
       * @param {string} event
       * @param {Function} handler
       */
      on: function (event, handler) {
        if (!global.eave.eventHandlers[event]) {
          global.eave.eventHandlers[event] = [];
        }

        global.eave.eventHandlers[event].push(handler);
      },

      /**
       * Remove a handler to no longer listen to the event. Must pass the same handler that was used when
       * attaching the event via ".on".
       * @param {string} event
       * @param {Function} handler
       */
      off: function (event, handler) {
        if (!global.eave.eventHandlers[event]) {
          return;
        }

        var i = 0;
        for (i; i < global.eave.eventHandlers[event].length; i++) {
          if (global.eave.eventHandlers[event][i] === handler) {
            global.eave.eventHandlers[event].splice(i, 1);
          }
        }
      },

      /**
       * Triggers the given event and passes the parameters to all handlers.
       *
       * @param {string} event
       * @param {Array} extraParameters
       * @param {Object} context  If given the handler will be executed in this context
       */
      trigger: function (event, extraParameters, context) {
        if (!global.eave.eventHandlers[event]) {
          return;
        }

        var i = 0;
        for (i; i < global.eave.eventHandlers[event].length; i++) {
          global.eave.eventHandlers[event][i].apply(
            context || global.eave.windowAlias,
            extraParameters,
          );
        }
      },

      /**
       * Add plugin
       *
       * @param {string} pluginName
       * @param {Object} pluginObj
       */
      addPlugin: function (pluginName, pluginObj) {
        global.eave.plugins[pluginName] = pluginObj;
      },

      /**
       * Get Tracker (factory method)
       *
       * @param {string} eaveUrl
       * @param {int|string} siteId
       * @returns {Tracker}
       */
      getTracker: function (eaveUrl, siteId) {
        if (!h.isDefined(siteId)) {
          siteId = this.getAsyncTracker().getSiteId();
        }
        if (!h.isDefined(eaveUrl)) {
          eaveUrl = this.getAsyncTracker().getTrackerUrl();
        }

        return new Tracker(eaveUrl, siteId);
      },

      /**
       * Get all created async trackers
       *
       * @returns {Tracker[]}
       */
      getAsyncTrackers: function () {
        return global.eave.asyncTrackers;
      },

      /**
       * Adds a new tracker. All sent requests will be also sent to the given siteId and eaveUrl.
       * If eaveUrl is not set, current url will be used.
       *
       * @param {null|string} eaveUrl  If null, will reuse the same tracker URL of the current tracker instance
       * @param {int|string} siteId
       * @returns {Tracker}
       */
      addTracker: function (eaveUrl, siteId) {
        var tracker;
        if (!global.eave.asyncTrackers.length) {
          tracker = createFirstTracker(eaveUrl, siteId);
        } else {
          tracker = global.eave.asyncTrackers[0].addTracker(eaveUrl, siteId);
        }
        return tracker;
      },

      /**
       * Get internal asynchronous tracker object.
       *
       * If no parameters are given, it returns the internal asynchronous tracker object. If a eaveUrl and idSite
       * is given, it will try to find an optional
       *
       * @param {string} eaveUrl
       * @param {int|string} siteId
       * @returns {Tracker}
       */
      getAsyncTracker: function (eaveUrl, siteId) {
        var firstTracker;
        if (
          global.eave.asyncTrackers &&
          global.eave.asyncTrackers.length &&
          global.eave.asyncTrackers[0]
        ) {
          firstTracker = global.eave.asyncTrackers[0];
        } else {
          return createFirstTracker(eaveUrl, siteId);
        }

        if (!siteId && !eaveUrl) {
          // for BC and by default we just return the initially created tracker
          return firstTracker;
        }

        // we look for another tracker created via `addTracker` method
        if ((!h.isDefined(siteId) || null === siteId) && firstTracker) {
          siteId = firstTracker.getSiteId();
        }

        if ((!h.isDefined(eaveUrl) || null === eaveUrl) && firstTracker) {
          eaveUrl = firstTracker.getTrackerUrl();
        }

        var tracker,
          i = 0;
        for (i; i < global.eave.asyncTrackers.length; i++) {
          tracker = global.eave.asyncTrackers[i];
          if (
            tracker &&
            String(tracker.getSiteId()) === String(siteId) &&
            tracker.getTrackerUrl() === eaveUrl
          ) {
            return tracker;
          }
        }
      },

      /**
       * NOTE: not sure if this is relevant since matomo fork
       * When calling plugin methods via "global.eave._paq.push(['...'])" and the plugin is loaded separately because
       * eave.js is not writable then there is a chance that first eave.js is loaded and later the plugin.
       * In this case we would have already executed all "global.eave._paq.push" methods and they would not have succeeded
       * because the plugin will be loaded only later. In this case, once a plugin is loaded, it should call
       * "eave.retryMissedPluginCalls()" so they will be executed after all.
       */
      retryMissedPluginCalls: function () {
        var missedCalls = global.eave.missedPluginTrackerCalls;
        global.eave.missedPluginTrackerCalls = [];
        var i = 0;
        for (i; i < missedCalls.length; i++) {
          h.apply(missedCalls[i]);
        }
      },
    };

    // Expose eave as an AMD module
    if (typeof define === "function" && define.amd) {
      define("eave", [], function () {
        return global.eave.eave;
      });
    }

    return global.eave.eave;
  })();
}

/* pluginTrackerHook */

(function () {
  "use strict";

  function hasPaqConfiguration() {
    if ("object" !== typeof global.eave._paq) {
      return false;
    }
    // needed to write it this way for jslint
    var lengthType = typeof global.eave._paq.length;
    if ("undefined" === lengthType) {
      return false;
    }

    return !!global.eave._paq.length;
  }

  if (
    window &&
    "object" === typeof window.eavePluginAsyncInit &&
    window.eavePluginAsyncInit.length
  ) {
    var i = 0;
    for (i; i < window.eavePluginAsyncInit.length; i++) {
      if (typeof window.eavePluginAsyncInit[i] === "function") {
        window.eavePluginAsyncInit[i]();
      }
    }
  }

  if (window && window.eaveAsyncInit) {
    window.eaveAsyncInit();
  }

  if (!window.eave.getAsyncTrackers().length) {
    // we only create an initial tracker when no other async tracker has been created yet in eaveAsyncInit()
    if (hasPaqConfiguration()) {
      // we only create an initial tracker if there is a configuration for it via global.eave._paq. Otherwise
      // eave.getAsyncTrackers() would return unconfigured trackers
      window.eave.addTracker();
    } else {
      global.eave._paq = {
        push: function (args) {
          // needed to write it this way for jslint
          var consoleType = typeof console;
          if (consoleType !== "undefined" && console && console.error) {
            console.error(
              "global.eave._paq.push() was used but eave tracker was not initialized before the eave.js file was loaded. Make sure to configure the tracker via global.eave._paq.push before loading eave.js. Alternatively, you can create a tracker via eave.addTracker() manually and then use global.eave._paq.push but it may not fully work as tracker methods may not be executed in the correct order.",
              args,
            );
          }
        },
      };
    }
  }

  window.eave.trigger("eaveInitialized", []);
  window.eave.initialized = true;
})();

/*jslint sloppy: true */
(function () {
  var jsTrackerType = typeof window.AnalyticsTracker;
  if (jsTrackerType === "undefined") {
    window.AnalyticsTracker = window.eave;
  }
})();
/*jslint sloppy: false */

/*! @license-end */
