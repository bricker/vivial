import { eaveLogger } from "../logging.js";
import { requestManager } from "../beacon.js";
import { CLICK_EVENT_TYPE, dispatchTriggerNotification } from "../internal/js-events.js";
import { StringMap, TargetProperties } from "../types.js";
import { castEventTargetToHtmlElement } from "../util/typechecking.js";
import { getElementAttributes } from "../util/dom-helpers.js";

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
  const timestamp = new Date().getTime();
  let eventTarget: TargetProperties | null = null;

  if (event.target) {
    const targetElement = castEventTargetToHtmlElement(event.target);

    if (targetElement) {
      const elementAttrs = getElementAttributes(targetElement);

      switch (targetElement.nodeName.toUpperCase()) {
        case "IMG":
          break;
        case "A":
          elementAttrs["innerText"] = targetElement.innerText;
          break;
        case "AREA":
          break;
        case "BUTTON":
          elementAttrs["innerText"] = targetElement.innerText;
          break;
        default:
          break;
      }

      eventTarget = {
        type: targetElement.nodeName.toUpperCase(),
        id: targetElement.id,
        attributes: elementAttrs,
      };
    }
  }

  const payload = await requestManager.buildPayload({
    event: {
      action: event.type,
      timestamp,
      seconds_elapsed: event.timeStamp,
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
  eaveLogger.debug("enabling click tracking");

  if (!initialized) {
    // This ensures that the handler isn't added more than once.
    // Although addEventListener won't add the same function object twice,
    // it's easy to accidentally add duplicate handlers by passing an anonymous function (eg arrow function).
    document.body.addEventListener(CLICK_EVENT_TYPE, trackClick, { capture: true, passive: true });
    document.body.addEventListener(CLICK_EVENT_TYPE, dispatchTriggerNotification, { capture: true, passive: true });
  }

  // TODO: Are these needed? Maybe for some browsers?
  // document.body.addEventListener("mouseup", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("mousedown", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("contextmenu", handleClick, { capture: true, passive: true });

  initialized = true;
}