import { AnalyticsBrowser } from "@segment/analytics-next";
import { isProdMode, myWindow } from "../types";

const analytics = AnalyticsBrowser.load({ writeKey: myWindow.app.segmentWriteKey! });

export enum EventName {
  CLICK = "click",
}

/**
 * Track a user action
 * https://segment.com/docs/connections/spec/track/
 *
 * @param eventName generic action name. (specifics of action target can be set in `extraProperties`)
 * @param extraProperties https://segment.com/docs/connections/spec/track/#properties
 */
export async function track(eventName: EventName, extraProperties?: object) {
  if (isProdMode) {
    await analytics.track(eventName, extraProperties);
  }
}

/**
 * Track a user viewing a page
 * https://segment.com/docs/connections/spec/page/
 *
 * @param category category of the page e.g. "Retail Page"
 * @param name name of specific page e.g. "Checkout"
 * @param extraProperties https://segment.com/docs/connections/spec/page/#properties
 */
export async function pageView(category?: string, name?: string, extraProperties?: object) {
  if (isProdMode) {
    await analytics.page(category, name, extraProperties);
  }
}

/**
 * Identify a user, associating all future tracking events with `userId`
 * https://segment.com/docs/connections/spec/identify/
 *
 * @param userId ID for a user (UUIDv4 from database recommended)
 * @param extraProperties https://segment.com/docs/connections/spec/identify/#custom-traits
 */
export async function identify(userId: string, extraProperties?: object) {
  await analytics.identify(userId, extraProperties);
}

/**
 * Get Segment anonymousId.
 * Will wait up to 0.5 seconds to recieve a value from Segement before rejecting.
 * Segment can have a null anonymousId value (temporarily) if none is found
 * in cookies + localStorage. Calling `anonymousId()` and receiving null triggers
 * setting a new value for future calls.
 * https://segment.com/docs/connections/sources/catalog/libraries/website/javascript/identity/#retrieve-the-anonymous-id
 */
export async function getVisitorId(): Promise<string> {
  const anonId = (await analytics.user()).anonymousId();
  if (anonId) {
    return anonId;
  }
  return new Promise((resolve, reject) => {
    let intervalCounter = 5;
    const interval = setInterval(async () => {
      const id = (await analytics.user()).anonymousId();
      if (id) {
        clearInterval(interval);
        resolve(id);
      } else {
        if (intervalCounter-- === 0) {
          reject();
        }
      }
    }, 100); // Check every 100ms
  });
}
