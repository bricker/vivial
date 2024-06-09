import { ScalarMap } from "../types.js";

export function getElementAttributes(element: Element): ScalarMap<string> {
  const attributes: ScalarMap<string> = {};

  for (const attr of element.attributes) {
    attributes[attr.name] = attr.value;
  }

  return attributes;
}
