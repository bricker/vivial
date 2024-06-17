/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-undef */

/**
 * This file contains environment variables defined in the Webpack config, and replaced by Webpack at compile time.
 */

// @ts-ignore: defined at compile time by webpack
// prettier-ignore
export const TRACKER_URL = WEBPACK_ENV_TRACKER_URL || "https://api.eave.fyi/public/ingest/browser";
