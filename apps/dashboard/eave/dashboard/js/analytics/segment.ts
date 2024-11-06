import { isProdMode, myWindow } from "../types";

export function track(eventName: string, data?: object) {
  if (isProdMode) {
    myWindow.analytics?.track(eventName, data);
  }
}

export function pageView(pageName?: string, data?: object) {
  if (isProdMode) {
    myWindow.analytics?.page(pageName, data);
  }
}

/** Segment anonymousId
 * https://segment.com/docs/connections/sources/catalog/libraries/website/javascript/identity/#retrieve-the-anonymous-id
 */
export async function getVisitorId(): Promise<string> {
  const anonId = myWindow.analytics?.user()?.anonymousId();
  if (anonId) {
    return anonId;
  }
  return new Promise((resolve, _reject) => {
    const interval = setInterval(() => {
      const id = myWindow.analytics?.user()?.anonymousId();
      if (id !== null) {
        clearInterval(interval);
        resolve(id);
      }
    }, 100); // Check every 100ms
  });
}
