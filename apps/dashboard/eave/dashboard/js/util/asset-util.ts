import { eaveWindow } from "../types";

export function imageUrl(filename: string): string {
  return `${eaveWindow.eave.assetBase}/images/${filename}`;
}

export function jsUrl(filename: string): string {
  return `${eaveWindow.eave.assetBase}/dist/${filename}`;
}
