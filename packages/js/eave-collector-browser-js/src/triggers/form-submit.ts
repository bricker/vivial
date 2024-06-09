import { requestManager } from "../beacon";
import { LOG_TAG } from "../internal/constants";
import { getElementAttributes } from "../util/dom-helpers";
import { currentTimestampSeconds } from "../util/timestamp.js";
import { castEventTargetToHtmlElement } from "../util/type-helpers";

export async function formSubmitEventHandler(event: SubmitEvent) {
  const timestamp = currentTimestampSeconds();
  const target = event.target;

  if (!target) {
    return;
  }

  const element = castEventTargetToHtmlElement<HTMLFormElement>(target);
  const nodeName = element?.nodeName.toUpperCase();

  if (!element || nodeName !== "FORM") {
    // The target is not an Element
    console.warn(LOG_TAG, "Invalid event target for form submit");
    return;
  }

  const attributes = getElementAttributes(element);

  const payload = await requestManager.buildPayload({
    action: event.type,
    timestamp,
    target: {
      type: nodeName,
      id: element.id,
      content: element.action,
      attributes: attributes,
    },
  });

  requestManager.queueEvent(payload);
}
