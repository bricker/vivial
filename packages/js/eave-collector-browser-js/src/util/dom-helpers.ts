import { StringMap } from "../types";

export function getElementAttributes(element: Element): StringMap<string> {
  const attrs: StringMap<string> = {};

  for (const attr of Array.from(element.attributes)) {
    attrs[attr.name] = attr.value;
  }

  return attrs;
}
