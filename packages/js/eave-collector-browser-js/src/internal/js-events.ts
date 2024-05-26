/// Eave events

export const EAVE_COOKIE_CONSENT_REVOKED_EVENT_TYPE = "eave.cookie_consent_revoked";
export const EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE = "eave.cookie_consent_granted";

export const EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE = "eave.tracking_consent_revoked";
export const EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE = "eave.tracking_consent_granted";

export const EAVE_TRIGGER_EVENT_TYPE = "eave.trigger";

/// DOM events

// https://developer.mozilla.org/en-US/docs/Web/API/Document/visibilitychange_event
export const VISIBILITY_CHANGE_EVENT_TYPE = "visibilitychange";

// https://developer.mozilla.org/en-US/docs/Web/API/Window/popstate_event
export const POPSTATE_EVENT_TYPE = "popstate";

// https://developer.mozilla.org/en-US/docs/Web/API/Window/hashchange_event
export const HASHCHANGE_EVENT_TYPE = "hashchange";

// https://developer.mozilla.org/en-US/docs/Web/API/HTMLFormElement/submit_event
export const SUBMIT_EVENT_TYPE = "submit";

// https://developer.mozilla.org/en-US/docs/Web/API/Element/click_event
export const CLICK_EVENT_TYPE = "click";

/**
 * Dispatches the EAVE_TRIGGER_EVENT_TYPE event on the window.
 * This function is meant to be passed directly to addEventListener.
 */
export function dispatchTriggerNotification(_evt: Event) {
  const event = new Event(EAVE_TRIGGER_EVENT_TYPE);
  window.dispatchEvent(event);
}