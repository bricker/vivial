export function getElementAttributes(element: Element): [string, string][] {
  return Array.from(element.attributes).map((attr) => [attr.name, attr.value]);
}
