/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-undef */
// @ts-nocheck: WEBPACK_ENV_* defined at compile time by webpack

/**
 * This file contains environment variables defined in the Webpack config, and replaced by Webpack at compile time.
 */

// prettier-ignore
const ingestUrlBase = WEBPACK_ENV_EAVE_API_BASE_URL || "https://api.eave.fyi/";
const logUrlPath = "public/ingest/log";
let u = new URL(ingestUrlBase);
u.pathname = u.pathname + logUrlPath;
export const LOG_TRACKER_URL = u.href;

const atomUrlPath = "public/ingest/browser";
u = new URL(ingestUrlBase);
u.pathname = u.pathname + atomUrlPath;
export const ATOM_TRACKER_URL = u.href;

export const MODE = WEBPACK_ENV_MODE || "production";
