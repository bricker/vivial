// @ts-check

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

import content from "./content.mjs";
import "./main.mjs";
import * as h from "./helpers.mjs";
import { Tracker } from "./tracker.mjs";
import { isVisible } from "./visibility.mjs";
// eslint-disable-next-line no-unused-vars
import * as Types from "./types.mjs";

/** @type {Types.GlobalEaveWindow} */
// @ts-ignore - We already set the `eave` property but this code doesn't know that.
const eaveWindow = window;

// eave singleton and namespace
if (typeof eaveWindow.eave.tracker !== "object") {
  eaveWindow.eave.tracker = (function () {
    "use strict";

    function TrackerProxy() {
      return {
        ...Array.prototype,
        push: h.apply, // Warning: This overrides the `push` function in an incompatible way. typechecking must be ignored as it relates to this function.
      };
    }

    /**
     * Applies the given methods in the given order if they are present in paq.
     *
     * @param {Array} paq
     * @param {Array} methodsToApply an array containing method names in the order that they should be applied
     *                 eg ['setSiteId', 'setTrackerUrl']
     *
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
                    ' is registered more than once in "eaveWindow.eave.settings" variable. Only the last call has an effect. Please have a look at the multiple eave trackers documentation: https://developer.matomo.org/guides/tracking-javascript-guide#multiple-piwik-trackers',
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

    // priority order for application of Tracker methods
    var applyFirst = [
      "addTracker",
      "enableFileTracking",
      "forgetCookieConsentGiven",
      "requireCookieConsent",
      "disableBrowserFeatureDetection",
      "disableCampaignParameters",
      "disableCookies",
      "setTrackingCookies",
      "setTrackerUrl",
      "setAPIUrl",
      "enableCrossDomainLinking",
      "setCrossDomainLinkingTimeout",
      "setDomains",
      "setUserId",
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
      eaveWindow.eave.asyncTrackers.push(tracker);

      eaveWindow.eave.settings = applyMethodsInOrder(
        eaveWindow.eave.settings,
        applyFirst,
      );

      // apply the queue of actions
      for (
        var iterator = 0;
        iterator < eaveWindow.eave.settings.length;
        iterator++
      ) {
        if (eaveWindow.eave.settings[iterator]) {
          h.apply(eaveWindow.eave.settings[iterator]);
        }
      }

      // replace initialization array with proxy object
      // @ts-ignore
      eaveWindow.eave.settings = TrackerProxy();

      eaveWindow.eave.tracker.trigger("TrackerAdded", [tracker]);

      return tracker;
    }

    /************************************************************
     * Proxy object
     * - this allows the caller to continue push()'ing to eaveWindow.eave.settings
     *   after the Tracker has been initialized and loaded
     ************************************************************/

    // initialize the eave singleton
    window.addEventListener(
      "beforeunload",
      h.beforeUnloadHandler,
      false,
    );
    window.addEventListener(
      "visibilitychange",
      function () {
        // if unloaded, return
        if (eaveWindow.eave.isPageUnloading) {
          return;
        }
        // if not visible
        if (document.visibilityState === "hidden") {
          h.executePluginMethod("unload");
        }
      },
      false,
    );
    window.addEventListener(
      "online",
      function () {
        if (h.isDefined(navigator.serviceWorker)) {
          navigator.serviceWorker.ready.then(
            function (swRegistration) {
              // @ts-ignore - ServiceWorkerRegistration.sync isn't supported by Firefox or Safari
              if (swRegistration && swRegistration.sync) {
                // @ts-ignore
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

    window.addEventListener(
      "message",
      function (e) {
        if (!e || !e.origin) {
          return;
        }

        let tracker;
        let eaveHost;
        const originHost = h.getHostName(e.origin);
        const trackers = eaveWindow.eave.eave?.getAsyncTrackers?.();

        if (!trackers) {
          return;
        }

        for (let i = 0; i < trackers.length; i++) {
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

        let data = null;
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
          const iframes =
            document.getElementsByTagName("iframe");
          for (let i = 0; i < iframes.length; i++) {
            const iframe = iframes[i];
            const iframeHost = h.getHostName(iframe.src);

            if (
              iframe.contentWindow &&
              h.isDefined(iframe.contentWindow.postMessage) &&
              iframeHost === originHost
            ) {
              const jsonMessage = JSON.stringify(postMessage);
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
          const trackers = eaveWindow.eave.eave?.getAsyncTrackers?.();
          if (!trackers) {
            return;
          }

          for (let i = 0; i < trackers.length; i++) {
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

    /************************************************************
     * Public data and methods
     ************************************************************/

    eaveWindow.eave.eave = {
      initialized: false,

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
          const captureType = typeof useCapture;
          if (captureType === "undefined") {
            useCapture = false;
          }

          element.addEventListener(eventType, eventHandler, useCapture);
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
        if (!eaveWindow.eave.eventHandlers[event]) {
          eaveWindow.eave.eventHandlers[event] = [];
        }

        eaveWindow.eave.eventHandlers[event].push(handler);
      },

      /**
       * Remove a handler to no longer listen to the event. Must pass the same handler that was used when
       * attaching the event via ".on".
       * @param {string} event
       * @param {Function} handler
       */
      off: function (event, handler) {
        if (!eaveWindow.eave.eventHandlers[event]) {
          return;
        }

        var i = 0;
        for (i; i < eaveWindow.eave.eventHandlers[event].length; i++) {
          if (eaveWindow.eave.eventHandlers[event][i] === handler) {
            eaveWindow.eave.eventHandlers[event].splice(i, 1);
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
        if (!eaveWindow.eave.eventHandlers[event]) {
          return;
        }

        for (let i = 0; i < eaveWindow.eave.eventHandlers[event].length; i++) {
          eaveWindow.eave.eventHandlers[event][i].apply(
            context || window,
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
        eaveWindow.eave.plugins[pluginName] = pluginObj;
      },

      /**
       * Get Tracker (factory method)
       *
       * @param {string} eaveUrl
       * @param {number | string} siteId
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
        return eaveWindow.eave.asyncTrackers;
      },

      /**
       * Adds a new tracker. All sent requests will be also sent to the given siteId and eaveUrl.
       * If eaveUrl is not set, current url will be used.
       *
       * @param {null|string} eaveUrl  If null, will reuse the same tracker URL of the current tracker instance
       * @param {number | string} siteId
       * @returns {Tracker}
       */
      addTracker: function (eaveUrl, siteId) {
        let tracker;
        if (!eaveWindow.eave.asyncTrackers.length) {
          tracker = createFirstTracker(eaveUrl, siteId);
        } else {
          tracker = eaveWindow.eave.asyncTrackers[0].addTracker(
            eaveUrl,
            siteId,
          );
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
       * @param {number | string} siteId
       * @returns {Tracker}
       */
      getAsyncTracker: function (eaveUrl, siteId) {
        let firstTracker;
        if (
          eaveWindow.eave.asyncTrackers &&
          eaveWindow.eave.asyncTrackers.length &&
          eaveWindow.eave.asyncTrackers[0]
        ) {
          firstTracker = eaveWindow.eave.asyncTrackers[0];
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

        let tracker;

        for (let i = 0; i < eaveWindow.eave.asyncTrackers.length; i++) {
          tracker = eaveWindow.eave.asyncTrackers[i];
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
       * When calling plugin methods via "eaveWindow.eave.settings.push(['...'])" and the plugin is loaded separately because
       * eave.js is not writable then there is a chance that first eave.js is loaded and later the plugin.
       * In this case we would have already executed all "eaveWindow.eave.settings.push" methods and they would not have succeeded
       * because the plugin will be loaded only later. In this case, once a plugin is loaded, it should call
       * "eave.retryMissedPluginCalls()" so they will be executed after all.
       */
      retryMissedPluginCalls: function () {
        const missedCalls = eaveWindow.eave.missedPluginTrackerCalls;
        eaveWindow.eave.missedPluginTrackerCalls = [];
        for (let i = 0; i < missedCalls.length; i++) {
          h.apply(missedCalls[i]);
        }
      },
    };

    // Expose eave as an AMD module
    if (typeof define === "function" && define.amd) {
      define("eave", [], function () {
        return eaveWindow.eave.eave;
      });
    }

    return eaveWindow.eave.eave;
  })();
}

/* pluginTrackerHook */

(function () {
  "use strict";

  function hasPaqConfiguration() {
    if ("object" !== typeof eaveWindow.eave.settings) {
      return false;
    }
    // needed to write it this way for jslint
    const lengthType = typeof eaveWindow.eave.settings.length;
    if ("undefined" === lengthType) {
      return false;
    }

    return !!eaveWindow.eave.settings.length;
  }

  if (
    window &&
    "object" === typeof eaveWindow.eave.trackerPluginAsyncInit &&
    eaveWindow.eave.trackerPluginAsyncInit.length
  ) {
    for (let i = 0; i < eaveWindow.eave.trackerPluginAsyncInit.length; i++) {
      if (typeof eaveWindow.eave.trackerPluginAsyncInit[i] === "function") {
        eaveWindow.eave.trackerPluginAsyncInit[i]();
      }
    }
  }

  if (window && eaveWindow.eave.trackerAsyncInit) {
    eaveWindow.eave.trackerAsyncInit();
  }

  if (!eaveWindow.eave.eave.getAsyncTrackers().length) {
    // we only create an initial tracker when no other async tracker has been created yet in eaveAsyncInit()
    if (hasPaqConfiguration()) {
      // we only create an initial tracker if there is a configuration for it via eaveWindow.eave.settings. Otherwise
      // eave.getAsyncTrackers() would return unconfigured trackers
      eaveWindow.eave.eave.addTracker();
    } else {
      eaveWindow.eave.settings = {
        push: function (args) {
          // needed to write it this way for jslint
          var consoleType = typeof console;
          if (consoleType !== "undefined" && console && console.error) {
            console.error(
              "eaveWindow.eave.settings.push() was used but eave tracker was not initialized before the eave.js file was loaded. Make sure to configure the tracker via eaveWindow.eave.settings.push before loading eave.js. Alternatively, you can create a tracker via eave.addTracker() manually and then use eaveWindow.eave.settings.push but it may not fully work as tracker methods may not be executed in the correct order.",
              args,
            );
          }
        },
      };
    }
  }

  eaveWindow.eave.tracker.trigger("eaveInitialized", []);
  eaveWindow.eave.tracker.initialized = true;
})();

/*jslint sloppy: false */

/*! @license-end */
