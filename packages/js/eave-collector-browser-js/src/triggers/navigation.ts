import { requestManager } from "../beacon";
import { LOG_TAG } from "../internal/constants";
import { currentTimestampSeconds } from "../util/timestamp";

const NAVIGATION_ACTION_NAME = "PAGE_VIEW";

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

  // prevent statechange event from double firing on initial page view
  // (url is undefined on initial page load)
  if (url !== null && url !== undefined) {
    const payload = await requestManager.buildPayload({
      action: NAVIGATION_ACTION_NAME,
      timestamp,
      target: null,
      extra: {
        reason: "statechange",
        state,
        url: url.toString(),
      },
    });

    requestManager.queueEvent(payload);
  }
}

/**
 * Tracks route-change history for single page applications, since
 * normal page view events aren't triggered for navigation without a GET request.
 */
export function wrapNavigationStateChangeFunctions() {
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
