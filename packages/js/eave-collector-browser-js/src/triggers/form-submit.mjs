// @ts-check

import { requestManager } from "../managers/beacon.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { sessionManager } from "../managers/session.mjs";
import { SESSION_EXTENDED_EVENT_TYPE, SUBMIT_EVENT_TYPE } from "../internal/event-types.mjs";
import { castEventTargetToHtmlElement } from "../util/typechecking.mjs";
import * as Types from "../types.mjs";

/**
 * @param {SubmitEvent} event
 *
 * @noreturn
 */
async function trackFormSubmit(event) {
  const timestamp = new Date();
  const target = event.target;

  if (!target) {
    return;
  }

  const element = castEventTargetToHtmlElement(target);
  if (element?.nodeName.toUpperCase() !== "FORM") {
    // The target is not an Element
    eaveLogger.warn("Invalid event target for form submit");
    return;
  }

  /** @type {Types.StringMap<string>} */
  const attributes = {};

  for (const attr of element.attributes) {
    attributes[attr.name] = attr.value;
  }

  const payload = await requestManager.buildPayloadFromEvent({
    event,
    timestamp,
    target: {
      target_type: element.nodeName,
      target_id: element.id,
      target_attributes: attributes,
    },
  });

  requestManager.sendEvent(payload);
}

/**
 * Track form submission events
 *
 * @noreturn
 */
export function enableFormTracking() {
  eaveLogger.debug("enabling form tracking");

  document.body.addEventListener(SUBMIT_EVENT_TYPE, trackFormSubmit, { capture: true, passive: true });
  document.body.addEventListener(SUBMIT_EVENT_TYPE, (_event) => sessionManager.resetOrExtendSession(), { capture: true, passive: true });
};