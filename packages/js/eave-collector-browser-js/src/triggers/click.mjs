// @ts-check

import { castEventTargetToHtmlElement, getElementAttributes } from "../helpers.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { requestManager } from "../managers/beacon.mjs";

/**
 * https://developer.mozilla.org/en-US/docs/Web/API/MouseEvent/button
 *
 * @param {MouseEvent} event
 *
 * @returns {string}
 */
function getNameOfClickedMouseButton(event) {
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
 *
 * @param {MouseEvent} event
 *
 * @noreturn
 */
async function handleClick(event) {
  const timestamp = new Date();
  let /** @type {{[key:string]: string}} */ elementAttrs = {};

  const targetElement = castEventTargetToHtmlElement(event.target);

  if (targetElement) {
    elementAttrs = getElementAttributes(targetElement);
    switch (targetElement.nodeName.toUpperCase()) {
      case "IMG":
        break;
      case "A":
        elementAttrs.innerText = targetElement.innerText;
        break;
      case "AREA":
        break;
      case "BUTTON":
        elementAttrs.innerText = targetElement.innerText;
        break;
      default:
        break;
    }
  }

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
    extra: {
      mouse_button: getNameOfClickedMouseButton(event),
    },
  });

  requestManager.sendEvent(payload);
}

/**
 * @noreturn
 */
export function enableClickTracking() {
  eaveLogger.debug("enabling click tracking");

  document.body.addEventListener("click", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("mouseup", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("mousedown", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("contextmenu", handleClick, { capture: true, passive: true });
};