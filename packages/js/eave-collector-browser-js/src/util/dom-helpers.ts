import { ScalarMap } from "../types.js";

export function getElementAttributes(element: Element): ScalarMap<string> {
  const attributes: ScalarMap<string> = {};

  for (const attr of element.attributes) {
    attributes[attr.name] = attr.value;
  }

  return attributes;
}

export function getClickableParentElement(startElement: HTMLElement | null): HTMLElement | null {
  // climb up DOM to find any wrapping anchor or button element
  let currElement: HTMLElement | null = startElement;
  let nodeName: string | undefined = currElement?.nodeName.toUpperCase();
  while (currElement && !(nodeName === "A" || nodeName === "BUTTON")) {
    currElement = currElement.parentElement;
    nodeName = currElement?.nodeName.toUpperCase();
  }

  return currElement;
}
