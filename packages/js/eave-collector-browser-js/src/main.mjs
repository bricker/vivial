// @ts-check
import * as Types from "./types.mjs";

// use existing _settings settings if available

const _settings = [];
_settings.push(["setTrackingCookies"]);
_settings.push(["trackPageView"]);
_settings.push(["enableLinkTracking"]);
_settings.push(["enableRouteHistoryTracking"]);
_settings.push(["enableButtonClickTracking"]);
_settings.push(["enableFormTracking"]);
_settings.push(["enableImageClickTracking"]);

// PRODUCTION is a custom webpack plugin defined in the webpack.config.cjs file as
// a boolean describing whether the script was compiled with mode=production
// @ts-ignore
const trackerUrl = PRODUCTION // eslint-disable-line no-undef
  ? "https://api.eave.dev/public/ingest/browser"
  : "http://api.eave.run:8080/public/ingest/browser";
_settings.push(["setTrackerUrl", trackerUrl]);

/** @type {Types.GlobalEaveWindow} */
// @ts-ignore - This line just declares the type of this variable for the typescript compiler. The `eave` property is missing, but we'll add it next.
const _window = window;

_window.eave = {
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
