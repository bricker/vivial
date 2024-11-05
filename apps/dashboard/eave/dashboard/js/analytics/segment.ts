import { myWindow } from "../types";

// TODO: dont fire analytics when running locally
export function track(eventName: string, data?: object) {
  myWindow.app.analytics?.track(eventName, data);
}

export function page(pageName?: string, data?: object) {
  myWindow.app.analytics?.page(pageName, data);
}
