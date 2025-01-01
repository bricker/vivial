export const VIVIAL_COOKIE_PREFIX = "vivial.";

export enum CookieId {
  Reroll = `${VIVIAL_COOKIE_PREFIX}reroll`,
  OutingMemory = `${VIVIAL_COOKIE_PREFIX}outing_memory`,
}

export interface RerollCookie {
  rerolls: number;
  expires: Date;
}

export interface OutingMemorySegment {
  id: string;
  expires: string;
}

export interface OutingMemoryCookie {
  excludedEventbriteEventSegments: OutingMemorySegment[];
  excludedEvergreenActivitySegments: OutingMemorySegment[];
  excludedGooglePlaceSegments: OutingMemorySegment[];
}
