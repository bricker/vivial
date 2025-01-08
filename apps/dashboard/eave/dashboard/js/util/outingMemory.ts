import { ActivitySource, Outing, PlanOutingInput } from "../graphql/generated/graphql";
import { CookieId, OutingMemoryCookie, OutingMemorySegment } from "../types/cookie";
import { in1Year, in24Hours, isExpired } from "./date";

function getOutingMemoryCookie(): OutingMemoryCookie | null {
  if (document.cookie) {
    const cookieArray = document.cookie.split(";");
    for (let i = 0; i < cookieArray.length; i++) {
      const cookie = cookieArray[i];
      if (cookie) {
        const [key, value] = cookie.trim().split("=");
        if (key === CookieId.OutingMemory && value) {
          return JSON.parse(value) as OutingMemoryCookie;
        }
      }
    }
  }
  return null;
}

function setOutingMemoryCookie(value: OutingMemoryCookie) {
  const expires = in1Year().toUTCString();
  document.cookie = `${CookieId.OutingMemory}=${JSON.stringify(value)}; expires=${expires}; path=/`;
}

function initOutingMemory(): OutingMemoryCookie {
  const outingMemory: OutingMemoryCookie = {
    excludedEventbriteEventSegments: [],
    excludedEvergreenActivitySegments: [],
    excludedGooglePlaceSegments: [],
  };

  return outingMemory;
}

function purgeOutingMemory(outingMemory: OutingMemoryCookie) {
  outingMemory.excludedEventbriteEventSegments = outingMemory.excludedEventbriteEventSegments.filter(
    (s) => !isExpired(new Date(s.expires)),
  );
  outingMemory.excludedEvergreenActivitySegments = outingMemory.excludedEvergreenActivitySegments.filter(
    (s) => !isExpired(new Date(s.expires)),
  );
  outingMemory.excludedGooglePlaceSegments = outingMemory.excludedGooglePlaceSegments.filter(
    (s) => !isExpired(new Date(s.expires)),
  );
  setOutingMemoryCookie(outingMemory);
}

export function appendOutingMemory(input: PlanOutingInput) {
  const outingMemory = getOutingMemoryCookie();
  if (outingMemory) {
    // Remove expired outing segments from memory before appending.
    purgeOutingMemory(outingMemory);

    // Append excluded activity / restaurant Ids to planOuting input.
    input.excludedEventbriteEventIds = outingMemory.excludedEventbriteEventSegments.map((x) => x.id);
    input.excludedGooglePlaceIds = outingMemory.excludedGooglePlaceSegments.map((x) => x.id);
    input.excludedEvergreenActivityIds = outingMemory.excludedEvergreenActivitySegments.map((x) => x.id);
  }
}

export function updateOutingMemory(outing: Outing) {
  const outingMemory = getOutingMemoryCookie() || initOutingMemory();
  const restaurant = outing.reservation?.restaurant;
  if (restaurant) {
    outingMemory.excludedGooglePlaceSegments.push({
      id: restaurant.sourceId,
      expires: in24Hours().toUTCString(),
    });
  }
  const activity = outing.activityPlan?.activity;
  if (activity) {
    const segment: OutingMemorySegment = {
      id: activity.sourceId,
      expires: in24Hours().toUTCString(),
    };
    switch (activity.source) {
      case ActivitySource.GooglePlaces:
        outingMemory.excludedGooglePlaceSegments.push(segment);
        break;
      case ActivitySource.Eventbrite:
        outingMemory.excludedEventbriteEventSegments.push(segment);
        break;
      case ActivitySource.Internal:
        outingMemory.excludedEvergreenActivitySegments.push(segment);
        break;
      default:
        break;
    }
  }
  setOutingMemoryCookie(outingMemory);
}
