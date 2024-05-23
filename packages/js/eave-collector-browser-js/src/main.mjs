// @ts-check

import * as Types from "./types.mjs"; // eslint-disable-line no-unused-vars

// @ts-ignore - this is a known global variable implicitly set on the window.
export const /** @type {string | undefined} */ clientId = EAVE_CLIENT_ID; // eslint-disable-line no-undef

export const /** @type {Types.GlobalEaveProperties} */ eave = {
  clientId,
  pageViewId: crypto.randomUUID(),
};
