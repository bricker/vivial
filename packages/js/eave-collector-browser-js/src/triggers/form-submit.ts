import { requestManager } from "../beacon.js";
import { eaveLogger } from "../logging.js";
import { SUBMIT_EVENT_TYPE, dispatchTriggerNotification } from "../internal/js-events.js";
import { castEventTargetToHtmlElement } from "../util/typechecking.js";
import { getElementAttributes } from "../util/dom-helpers.js";
import { EventProperties } from "../types.js";

async function trackFormSubmit(event: SubmitEvent) {
  const timestamp = new Date().getTime();
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

  const attributes = getElementAttributes(element);

  const submitter = event.submitter;
  if (submitter) {
    attributes["button_text"] = submitter.innerText;
  }

  const payload = await requestManager.buildPayload({
    event: {
      action: event.type,
      timestamp,
      seconds_elapsed: event.timeStamp,
      target: {
        type: element.nodeName,
        id: element.id,
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
  eaveLogger.debug("enabling form tracking");

  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    document.body.addEventListener(SUBMIT_EVENT_TYPE, trackFormSubmit, { capture: true, passive: true });
    document.body.addEventListener(SUBMIT_EVENT_TYPE, dispatchTriggerNotification, { capture: true, passive: true });
  }

  initialized = true;
}