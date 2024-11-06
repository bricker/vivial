import { isProdMode, myWindow } from "../types";

export function track(eventName: string, data?: object) {
  if (isProdMode) {
    myWindow.app.analytics?.track(eventName, data);
  }
}

export function page(pageName?: string, data?: object) {
  if (isProdMode) {
    myWindow.app.analytics?.page(pageName, data);
  }
}
