export const VIVIAL_COOKIE_PREFIX = "vivial.";

export enum CookieId {
  Reroll = `${VIVIAL_COOKIE_PREFIX}reroll`,
}

export interface RerollCookie {
  rerolls: number;
  expires: Date;
}
