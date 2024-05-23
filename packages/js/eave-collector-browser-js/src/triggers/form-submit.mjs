// @ts-check

import { requestManager } from "../managers/beacon.mjs";
import { castEventTargetToHtmlElement } from "../helpers.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import * as Types from "../types.mjs";

/**
 * @param {SubmitEvent} event
 *
 * @noreturn
 */
async function handleFormSubmit(event) {
  const timestamp = new Date();

  const target = event.target;

  if (!target) {
    return;
  }

  if (event.type !== "submit") {
    eaveLogger.warn("Invalid event type for form submit", event.type);
    return;
  }

  const element = castEventTargetToHtmlElement(target);
  if (element?.nodeName.toUpperCase() !== "FORM") {
    // The target is not an Element
    eaveLogger.warn("Invalid event target for form submit");
    return;
  }

  const /** @type {{[key: string]: string}} */ attributes = {};

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
  document.body.addEventListener("submit", handleFormSubmit, {
    capture: true,
    passive: false, // This is set to false because a form submission may reload the document.
  });
};