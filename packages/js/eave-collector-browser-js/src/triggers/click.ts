import { requestManager } from "../beacon";
import { TargetProperties } from "../types";
import { getElementAttributes } from "../util/dom-helpers";
import { currentTimestampSeconds } from "../util/timestamp";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

const CLICK_ACTION_NAME = "CLICK";

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
export async function clickEventHandler(event: MouseEvent) {
  const timestamp = currentTimestampSeconds();
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
        content: targetElement.innerText,
        attributes: elementAttrs,
      };
    }
  }

  const payload = await requestManager.buildPayload({
    action: CLICK_ACTION_NAME,
    timestamp,
    target: eventTarget,
    extra: {
      mouse_button: getNameOfClickedMouseButton(event),
    },
  });

  requestManager.queueEvent(payload);
}
