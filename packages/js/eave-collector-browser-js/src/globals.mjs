// @ts-check
import * as Types from "./types.js";

// use existing _settings settings if available

const _settings = [];
_settings.push(["setTrackingCookies"]);
_settings.push(["trackPageView"]);
_settings.push(["enableLinkTracking"]);
_settings.push(["enableRouteHistoryTracking"]);
_settings.push(["enableButtonClickTracking"]);
_settings.push(["enableFormTracking"]);

// PRODUCTION is a custom webpack plugin defined in the webpack.config.cjs file as
// a boolean describing whether the script was compiled with mode=production
// @ts-ignore
const trackerUrl = PRODUCTION // eslint-disable-line no-undef
  ? "https://api.eave.dev/public/ingest/browser"
  : "http://api.eave.run:8080/public/ingest/browser";
_settings.push(["setTrackerUrl", trackerUrl]);

/** @type {Types.GlobalEaveWindow} */
const _globalThis = globalThis;

_globalThis._eave = {
  expireDateTime: undefined,
  settings: _settings,
  plugins: {},
  eventHandlers: {},
  asyncTrackers: [],
  eave: undefined,
  missedPluginTrackerCalls: [],
  coreConsentCounter: 0,
  coreHeartBeatCounter: 0,
  trackerIdCounter: 0,
  isPageUnloading: false,
  trackerInstallCheckNonce: "",
};
