import { requestManager } from "../beacon";
import { LOG_TAG } from "../internal/constants";
import { currentTimestampSeconds } from "../util/timestamp";

const NAVIGATION_ACTION_NAME = "navigation";

export async function trackPageLoad() {
  const timestamp = currentTimestampSeconds();

  const payload = await requestManager.buildPayload({
    action: NAVIGATION_ACTION_NAME,
    timestamp,
    target: null,
    extra: {
      reason: "pageload",
    },
  });

  requestManager.queueEvent(payload);
}

export async function hashChangeEventHandler(evt: Event) {
  const timestamp = currentTimestampSeconds();

  const payload = await requestManager.buildPayload({
    action: NAVIGATION_ACTION_NAME,
    timestamp,
    target: null,
    extra: {
      reason: evt.type,
    },
  });

  requestManager.queueEvent(payload);
}

export async function popStateEventHandler(evt: PopStateEvent) {
  const timestamp = currentTimestampSeconds();

  const payload = await requestManager.buildPayload({
    action: NAVIGATION_ACTION_NAME,
    timestamp,
    target: null,
    extra: {
      reason: evt.type,
    },
  });

  requestManager.queueEvent(payload);
}

/**
 * @param state - The `state` parameter given to history.pushState/replaceState. Any serializable object.
 */
async function trackNavigationStateChange(state: any, url?: URL | string | null) {
  const timestamp = currentTimestampSeconds();

  const payload = await requestManager.buildPayload({
    action: NAVIGATION_ACTION_NAME,
    timestamp,
    target: null,
    extra: {
      reason: "statechange",
      state,
      url: url?.toString() || null,
    },
  });

  requestManager.queueEvent(payload);
}

// export async function trackHistoryChange(event) {
//   // if (
//   //   event &&
//   //   event.target &&
//   //   event.target.location &&
//   //   event.target.location.href
//   // ) {
//   //   return event.target.location.href;
//   // }
//   // return getCurrentUrl();

//   logPageView(
//     "", // TODO: make more meaningful
//     {
//       event: "HistoryChange",
//       historyChangeSource: newEvent.eventType,
//       oldUrl: origin + oldUrl,
//       newUrl: origin + nowUrl,
//       oldUrlHash: tmpLast.hash,
//       newUrlHash: newEvent.hash,
//       oldUrlPath: tmpLast.path,
//       newUrlPath: newEvent.path,
//       oldUrlSearch: tmpLast.search,
//       newUrlSearch: newEvent.search,
//       oldHistoryState: tmpLast.state,
//       newHistoryState: newEvent.state,
//     },
//   );

// }

/**
 * Tracks route-change history for single page applications, since
 * normal page view events aren't triggered for navigation without a GET request.
 */
export function wrapNavigationStateChangeFunctions() {
  // h.trackCallbackOnReady(function () {
  //   const initialUrl = getCurrentUrl();

  //   const theUrl = new URL(urlToParse);
  //   if (urlPart && urlPart in theUrl) {
  //     if ("hash" === urlPart) {
  //       return String(theUrl[urlPart]).replace("#", "");
  //     } else if ("protocol" === urlPart) {
  //       return String(theUrl[urlPart]).replace(":", "");
  //     } else if ("search" === urlPart) {
  //       return String(theUrl[urlPart]).replace("?", "");
  //     } else if ("port" === urlPart && !theUrl[urlPart]) {
  //       if (theUrl.protocol === "https:") {
  //         return "443";
  //       } else if (theUrl.protocol === "http:") {
  //         return "80";
  //       }
  //     }
  //     return theUrl[urlPart];
  //   }

  //   const origin = parseUrl(initialUrl, "origin");

  //   let lastEvent = {
  //     eventType: null,
  //     hash: parseUrl(initialUrl, "hash"),
  //     search: parseUrl(initialUrl, "search"),
  //     path: parseUrl(initialUrl, "pathname"),
  //   };

  //   function trigger(eventType, newUrl, newState) {

  //     const newEvent = {
  //       eventType: eventType,
  //       hash: parseUrl(newUrl, "hash"),
  //       search: parseUrl(newUrl, "search"),
  //       path: parseUrl(newUrl, "pathname"),
  //       state: newState,
  //     };

  //     let oldUrl = lastEvent.path;
  //     if (lastEvent.search) {
  //       oldUrl += "?" + lastEvent.search;
  //     }
  //     if (lastEvent.hash) {
  //       oldUrl += "#" + lastEvent.hash;
  //     }
  //     let nowUrl = newEvent.path;
  //     if (newEvent.search) {
  //       nowUrl += "?" + newEvent.search;
  //     }
  //     if (newEvent.hash) {
  //       nowUrl += "#" + newEvent.hash;
  //     }
  //     if (oldUrl !== nowUrl) {
  //       const tmpLast = lastEvent;
  //       lastEvent = newEvent; // overwrite as early as possible in case event gets triggered again

  //       trackCallback(function () {
  //       });
  //     }
  //   }

  // function replaceHistoryMethod(methodNameToReplace) {
  //   setMethodWrapIfNeeded(
  //     window.history,
  //     methodNameToReplace,
  //     function (state, _title, _urlParam) {
  //       trigger(methodNameToReplace, getCurrentUrl(), state);
  //     },
  //   );
  // }

  // React Router uses `pushState` and `replaceState` to update the history stack when it renders new pages.
  // However, it's important to note that `pushState` nor `replaceState` actually do any navigation.
  // Calling `pushState` or `replaceState` doesn't actually mean that the user has navigated to a new page.
  // This is therefore an imprecise way to track navigation in a SPA.
  // The "navigate" event would be a cleaner way to do this - but it is not widely supported yet (2024-05)
  // https://developer.mozilla.org/en-US/docs/Web/API/Navigation/navigate_event

  const originalPushState = window.history.pushState;
  window.history.pushState = function (state, unused, url) {
    // We use apply() here for the rare case where this function is called on a different object than is bound to `originalPushState`.
    const proxyValue = originalPushState.call(this, state, unused, url);
    trackNavigationStateChange(state, url).catch((e) => console.error(LOG_TAG, e));
    return proxyValue;
  };

  const originalReplaceState = window.history.replaceState;
  window.history.replaceState = function (state, unused, url) {
    // We use apply() here for the rare case where this function is called on a different object than is bound to `originalReplaceState`.
    const proxyValue = originalReplaceState.call(this, state, unused, url);
    trackNavigationStateChange(state, url).catch((e) => console.error(LOG_TAG, e));
    return proxyValue;
  };
}
