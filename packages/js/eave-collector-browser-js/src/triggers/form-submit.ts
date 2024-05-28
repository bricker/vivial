import { requestManager } from "../beacon";
import { eaveLogger } from "../logging";
import { SUBMIT_EVENT_TYPE, dispatchTriggerNotification } from "../internal/js-events";
import { castEventTargetToHtmlElement } from "../util/typechecking";
import { getElementAttributes } from "../util/dom-helpers";
import { EventProperties } from "../types";

async function trackFormSubmit(event: SubmitEvent) {
  const timestamp = Date.now();
  const target = event.target;

  if (!target) {
    return;
  }

  const element = castEventTargetToHtmlElement(target);
  const nodeName = element?.nodeName.toUpperCase();

  if (!element || nodeName !== "FORM") {
    // The target is not an Element
    eaveLogger.warn("Invalid event target for form submit");
    return;
  }

  const attributes = getElementAttributes(element);

  const payload = await requestManager.buildPayload({
    event: {
      action: event.type,
      timestamp: timestamp / 1000,
      origin_elapsed_ms: event.timeStamp,
      target: {
        type: nodeName,
        id: element.id,
        text: event.submitter?.innerText || null,
        attributes: attributes,
      },
    },
  });

  requestManager.queueEvent(payload);
}

let initialized = false;

/**
 * Track form submission events
 */
export function enableFormTracking() {
  eaveLogger.debug("Enabling form tracking.");

  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    document.body.addEventListener(SUBMIT_EVENT_TYPE, trackFormSubmit, { capture: true, passive: true });
    document.body.addEventListener(SUBMIT_EVENT_TYPE, dispatchTriggerNotification, { capture: true, passive: true });
  }

  initialized = true;
}