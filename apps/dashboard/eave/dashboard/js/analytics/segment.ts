import { AnalyticsBrowser } from "@segment/analytics-next";
import { myWindow } from "../types/window";
import { delay } from "../util/delay";

export const analytics = AnalyticsBrowser.load(
  { writeKey: myWindow.app.segmentWriteKey! },
  { disable: !myWindow.app.analyticsEnabled },
);

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
export async function track({ eventName, extraProperties }: { eventName: EventName; extraProperties?: object }) {
  if (myWindow.app.analyticsEnabled) {
    await analytics.track(eventName, extraProperties);
  } else {
    console.debug("track", eventName, extraProperties);
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
export async function pageView({
  category,
  name,
  extraProperties,
}: {
  category?: string;
  name?: string;
  extraProperties?: object;
}) {
  if (myWindow.app.analyticsEnabled) {
    await analytics.page(category, name, extraProperties);
  } else {
    console.debug("pageView", `category: ${category}`, `name: ${name}`, extraProperties);
  }
}

/**
 * Identify a user, associating all future tracking events with `userId`
 * https://segment.com/docs/connections/spec/identify/
 *
 * @param userId ID for a user (UUIDv4 from database recommended)
 * @param extraProperties https://segment.com/docs/connections/spec/identify/#custom-traits
 */
export async function identify({ userId, extraProperties }: { userId: string; extraProperties?: object }) {
  if (myWindow.app.analyticsEnabled) {
    await analytics.identify(userId, extraProperties);
  } else {
    console.debug("identify", userId, extraProperties);
  }
}

/**
 * Get Segment anonymousId.
 * Will wait up to 0.5 seconds to receive a value from Segment before rejecting.
 * Segment can have a null anonymousId value (temporarily) if none is found
 * in cookies + localStorage. Calling `anonymousId()` and receiving null triggers
 * setting a new value for future calls.
 * https://segment.com/docs/connections/sources/catalog/libraries/website/javascript/identity/#retrieve-the-anonymous-id
 */
export async function getVisitorId(): Promise<string> {
  let intervalCounter = 5;

  while (intervalCounter >= 0) {
    const user = await analytics.user();
    const anonId = user.anonymousId();
    if (anonId) {
      return anonId;
    }

    if (intervalCounter > 0) {
      intervalCounter--;
      await delay({ ms: 100 });
    }
  }

  throw new Error("failed to get visitor ID");
}

// track all click events
document.getElementsByTagName("body")[0]?.addEventListener("click", (ev: MouseEvent) => {
  const target = ev.target as HTMLElement | null;
  const tagName = target?.tagName || "BODY";
  let innerText: string | null | undefined = target?.innerText;
  if (tagName === "INPUT" || tagName === "FORM") {
    innerText = "[redacted]";
  }
  const placeholder = target?.getAttribute("placeholder");
  const href = target?.getAttribute("href");

  track({
    eventName: EventName.CLICK,
    extraProperties: {
      tagName,
      href,
      innerText,
      placeholder,
    },
  }).catch(() => {
    /* no-op */
  });
});
