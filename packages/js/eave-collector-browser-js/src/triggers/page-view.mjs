import { HASHCHANGE_EVENT_TYPE, POPSTATE_EVENT_TYPE, SESSION_EXTENDED_EVENT_TYPE } from "../internal/event-types.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { requestManager } from "../managers/beacon.mjs";
import { sessionManager } from "../managers/session.mjs";

/**
 * @noreturn
 */
export async function trackPageView() {
  const timestamp = new Date();
  sessionManager.resetOrExtendSession();

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
 * @param {HashChangeEvent} event
 *
 * @noreturn
 */
async function trackHashChange(event) {
  const timestamp = new Date();
  sessionManager.resetOrExtendSession();

  const newUrl = window.location;

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
 * @param {PopStateEvent} event
 *
 * @noreturn
 */
async function trackPopState(event) {
  const timestamp = new Date();
  sessionManager.resetOrExtendSession();

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
 * @param {object} state - The `state` parameter given to history.pushState/replaceState. Any serializable object.
 *
 * @noreturn
 */
async function trackNavigationStateChange(state) {
  const timestamp = new Date();
  sessionManager.resetOrExtendSession();

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

export async function trackHistoryChange(event) {
  // if (
  //   event &&
  //   event.target &&
  //   event.target.location &&
  //   event.target.location.href
  // ) {
  //   return event.target.location.href;
  // }
  // return getCurrentUrl();

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

}

/**
 * Tracks route-change history for single page applications, since
 * normal page view events aren't triggered for navigation without a GET request.
 *
 * @returns {string | undefined}
 */
function enableRouteHistoryTracking() {
  h.trackCallbackOnReady(function () {
    const initialUrl = getCurrentUrl();

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
        });
      }
    }

    // function replaceHistoryMethod(methodNameToReplace) {
    //   setMethodWrapIfNeeded(
    //     window.history,
    //     methodNameToReplace,
    //     function (state, _title, _urlParam) {
    //       trigger(methodNameToReplace, getCurrentUrl(), state);
    //     },
    //   );
    // }

    // The "navigate" event would be a cleaner way to do this - but it is not widely supported yet (2024-05)
    // https://developer.mozilla.org/en-US/docs/Web/API/Navigation/navigate_event

    const originalPushState = window.history.pushState;
    window.history.pushState = function (state, unused, url) {
      // We use apply() here for the rare case where this function is called on a different object than is bound to `originalPushState`.
      const proxyValue = originalPushState.call(this, state, unused, url);
      trackPageView();
      return proxyValue;
    };

    const originalReplaceState = window.history.replaceState;
    window.history.replaceState = function (state, unused, url) {
      // We use apply() here for the rare case where this function is called on a different object than is bound to `originalReplaceState`.
      const proxyValue = originalReplaceState.call(this, state, unused, url);
      trackPageView(state, url);
      return proxyValue;
    }
  });
}

export function enableNavigationTracking() {
  eaveLogger.debug("enabling navigationtracking");

  window.addEventListener(HASHCHANGE_EVENT_TYPE, trackHashChange, { capture: true, passive: true });
  window.addEventListener(HASHCHANGE_EVENT_TYPE, sessionManager.resetOrExtendSession, { capture: true, passive: true });

  window.addEventListener(POPSTATE_EVENT_TYPE, trackPopState, { capture: true, passive: true });
  window.addEventListener(POPSTATE_EVENT_TYPE, sessionManager.resetOrExtendSession, { capture: true, passive: true });
}