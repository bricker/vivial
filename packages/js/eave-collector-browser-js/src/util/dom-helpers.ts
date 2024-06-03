import { KeyValueArray } from "../types.js";

export function getElementAttributes(element: Element): KeyValueArray {
  return Array.from(element.attributes).map((attr) => ({ key: attr.name, value: attr.value }));
}
