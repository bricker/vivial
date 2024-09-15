/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-undef */
// @ts-nocheck: WEBPACK_ENV_* defined at compile time by webpack

/**
 * This file contains environment variables defined in the Webpack config, and replaced by Webpack at compile time.
 */

// prettier-ignore
const ingestUrlBase = WEBPACK_ENV_EAVE_API_BASE_URL || "https://api.eave.fyi";
const logUrl = new URL("/public/ingest/log", ingestUrlBase);
export const LOG_TRACKER_URL = logUrl.href;

const atomUrl = new URL("/public/ingest/browser", ingestUrlBase);
export const ATOM_TRACKER_URL = atomUrl.href;

export const MODE = WEBPACK_ENV_MODE || "production";
