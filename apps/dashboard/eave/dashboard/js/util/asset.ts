import { myWindow } from "$eave-dashboard/js/types/window";

export function imageUrl(filename: string): string {
  return `${myWindow.app.assetBase}/images/${filename}`;
}

export function jsUrl(filename: string): string {
  return `${myWindow.app.assetBase}/dist/${filename}`;
}
