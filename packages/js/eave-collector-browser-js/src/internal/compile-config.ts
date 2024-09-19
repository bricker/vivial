/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-undef */
// @ts-nocheck: WEBPACK_ENV_* defined at compile time by webpack

/**
 * This file contains environment variables defined in the Webpack config, and replaced by Webpack at compile time.
 */

// prettier-ignore
const ingestUrlBase = WEBPACK_ENV_EAVE_API_BASE_URL || "https://api.eave.fyi";
const logUrlPath = "/public/ingest/log";
const logUrl = new URL(ingestUrlBase);
logUrl.pathname = logUrl.pathname + logUrlPath;
export const LOG_TRACKER_URL = logUrl.href;

const atomUrlPath = "/public/ingest/browser";
const atomUrl = new URL(ingestUrlBase);
atomUrl.pathname = atomUrl.pathname + atomUrlPath;
export const ATOM_TRACKER_URL = atomUrl.href;

export const MODE = WEBPACK_ENV_MODE || "production";
