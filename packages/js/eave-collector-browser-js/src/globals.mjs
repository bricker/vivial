// have to do this check on browser globals to make Node.js env happy
var documentAlias = typeof document !== "undefined" ? document : {},
  navigatorAlias = typeof navigator !== "undefined" ? navigator : {},
  screenAlias = typeof screen !== "undefined" ? screen : {},
  windowAlias = typeof window !== "undefined" ? window : {};

// use existing _settings settings if available
var _settings =
  typeof windowAlias._settings !== "undefined" ? windowAlias._settings : [];
_settings.push(["setTrackingCookies"]);
_settings.push(["trackPageView"]);
_settings.push(["enableLinkTracking"]);
_settings.push(["enableRouteHistoryTracking"]);
_settings.push(["enableButtonClickTracking"]);
_settings.push(["enableFormTracking"]);
// PRODUCTION is a custom webpack plugin defined in the webpack.config.cjs file as
// a boolean describing whether the script was compiled with mode=production
// eslint-disable-next-line no-undef
const trackerUrl = PRODUCTION
  ? "https://api.eave.dev/public/ingest/browser"
  : "http://api.eave.run:8080/public/ingest/browser";
_settings.push(["setTrackerUrl", trackerUrl]);

globalThis.eave = {
  expireDateTime: undefined,
  _settings,
  /* plugins */
  plugins: {},
  eventHandlers: {},
  /* alias frequently used globals for added minification (NOT CURRENTLY WORKING, JUST MAKING ACCESS PATH LONGER) */
  documentAlias,
  navigatorAlias,
  windowAlias,
  screenAlias,
  /* performance timing */
  performanceAlias:
    windowAlias.performance ||
    windowAlias.mozPerformance ||
    windowAlias.msPerformance ||
    windowAlias.webkitPerformance,
  /* encode */
  encodeWrapper: windowAlias.encodeURIComponent,
  /* decode */
  decodeWrapper: windowAlias.decodeURIComponent,
  /* urldecode */
  urldecode: unescape,
  /* asynchronous tracker */
  asyncTrackers: [],
  /* local eave */
  eave: undefined,
  missedPluginTrackerCalls: [],
  coreConsentCounter: 0,
  coreHeartBeatCounter: 0,
  trackerIdCounter: 0,
  isPageUnloading: false,
  trackerInstallCheckNonce: "",
};
