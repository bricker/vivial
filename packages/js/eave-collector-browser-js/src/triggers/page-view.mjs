import { requestManager } from "../managers/beacon.mjs";

/**
 * Log visit to this page
 *
 * @noreturn
 */
export async function trackPageView() {
  const payload = await requestManager.buildPayloadFromEvent({
    event,
    timestamp,
    target: {
      target_type: targetElement?.nodeName.toUpperCase(),
      target_id: targetElement?.id,
      target_attributes: {
        ...elementAttrs,
      }
    },
  });

  requestManager.sendEvent(payload);
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