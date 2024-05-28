import { requestManager } from "../beacon";
import { CLICK_EVENT_TYPE, dispatchTriggerNotification } from "../internal/js-events";
import { eaveLogger } from "../logging";
import { TargetProperties } from "../types";
import { getElementAttributes } from "../util/dom-helpers";
import { castEventTargetToHtmlElement } from "../util/typechecking";

/**
 * https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/button
 */
function getNameOfClickedMouseButton(event: MouseEvent): string {
  switch (event.button) {
    case 0:
      return "primary";
    case 1:
      return "aux";
    case 2:
      return "secondary";
    case 3:
      return "fourth";
    case 4:
      return "fifth";
    default:
      return "unknown";
  }
}

/**
 * Handle click event
 */
async function trackClick(event: MouseEvent) {
  const timestamp = Date.now();
  let eventTarget: TargetProperties | null = null;

  if (event.target) {
    const targetElement = castEventTargetToHtmlElement(event.target);

    if (targetElement) {
      if (targetElement.attributes.getNamedItem("type")?.value === "password") {
        // never track a click on a password field.
        return;
      }

      const nodeName = targetElement.nodeName.toUpperCase();
      const elementAttrs = getElementAttributes(targetElement);

      // TODO: This is capturing the innerText for everything clicked, which is not OK.
      // It should be limited to things like A and BUTTON. Things like form inputs and divs should be excluded.
      eventTarget = {
        type: nodeName,
        id: targetElement.id,
        text: targetElement.innerText,
        attributes: elementAttrs,
      };
    }
  }

  const payload = await requestManager.buildPayload({
    event: {
      action: event.type,
      timestamp: timestamp / 1000,
      origin_elapsed_ms: event.timeStamp,
      target: eventTarget,
    },
    extra: {
      mouse_button: getNameOfClickedMouseButton(event),
    },
  });

  requestManager.queueEvent(payload);
}

let initialized = false;

export function enableClickTracking() {
  eaveLogger.debug("Enabling click tracking.");

  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    document.body.addEventListener(CLICK_EVENT_TYPE, trackClick, {
      capture: true,
      passive: true,
    });
    document.body.addEventListener(CLICK_EVENT_TYPE, dispatchTriggerNotification, { capture: true, passive: true });
  }

  // TODO: Are these needed? Maybe for some browsers?
  // document.body.addEventListener("mouseup", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("mousedown", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("contextmenu", handleClick, { capture: true, passive: true });

  initialized = true;
}
