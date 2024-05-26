import { ScreenProperties } from "../types.js";

export function getScreenProperties(): ScreenProperties {
  return {
    width: screen.width,
    height: screen.height,
    avail_width: screen.availWidth,
    avail_height: screen.availHeight,
  }
}