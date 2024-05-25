// @ts-check

import { getElementAttributes } from "../util/helpers.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { requestManager } from "../managers/beacon.mjs";
import { castEventTargetToHtmlElement } from "../types.mjs";
import { sessionManager } from "../managers/session.mjs";
import * as Types from "../types.mjs";
import { CLICK_EVENT_TYPE } from "../internal/event-types.mjs";

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
async function trackClick(event) {
  const timestamp = new Date();
  sessionManager.resetOrExtendSession();

  /** @type {Types.StringMap<string>} */
  let elementAttrs = {};

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

  document.body.addEventListener(CLICK_EVENT_TYPE, trackClick, { capture: true, passive: true });
  document.body.addEventListener(CLICK_EVENT_TYPE, sessionManager.resetOrExtendSession, { capture: true, passive: true });

  // document.body.addEventListener("mouseup", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("mousedown", handleClick, { capture: true, passive: true });
  // document.body.addEventListener("contextmenu", handleClick, { capture: true, passive: true });
};