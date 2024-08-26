/* eslint-disable @typescript-eslint/ban-ts-comment */
/* eslint-disable no-undef */

import path from "path";

/**
 * This file contains environment variables defined in the Webpack config, and replaced by Webpack at compile time.
 */

// @ts-nocheck: defined at compile time by webpack
// prettier-ignore
const ingestUrlBase = WEBPACK_ENV_INGEST_URL || "https://api.eave.fyi/public/ingest";
const logUrlPath = WEBPACK_ENV_LOG_URL_PATH || "/logs";
let u = new URL(ingestUrlBase);
u.pathname = path.join(u.pathname, logUrlPath);
export const LOG_TRACKER_URL = u.href;

const atomUrlPath = WEBPACK_ENV_ATOM_URL_PATH || "/browser";
u = new URL(ingestUrlBase);
u.pathname = path.join(u.pathname, logUrlPath);
export const ATOM_TRACKER_URL = u.href;

export const MODE = WEBPACK_ENV_MODE || "production";
