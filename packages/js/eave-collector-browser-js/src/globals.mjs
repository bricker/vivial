/**
 * 
 * @param {string} clientId 
 * 
 * @example
 * <script src="https://cdn.eave.fyi/browser.js"></script>
 * <script>
 *   initEave("your client id");
 * </script>
 */

// have to do this check on browser globals to make Node.js env happy
var documentAlias = typeof document !== "undefined" ? document : {},
  navigatorAlias = typeof navigator !== "undefined" ? navigator : {},
  screenAlias = typeof screen !== "undefined" ? screen : {},
  windowAlias = typeof window !== "undefined" ? window : {};

// use existing _settings settings if available
// eslint-disable-next-line no-use-before-define
var _settings = typeof _settings !== "undefined" ? _settings : [];
_settings.push(["setTrackingCookies"])
_settings.push(["trackPageView"]);
_settings.push(["enableLinkTracking"]);
_settings.push(["enableRouteHistoryTracking"]);
_settings.push(["enableButtonClickTracking"]);
_settings.push(["enableFormTracking"]);
// TODO: update to point to eave backend
// TODO: switch on env whether to send to prod or stage
// TODO: update post to send data in body
_settings.push(["setTrackerUrl", "http://api.eave.run:8080/public/ingest/browser"]);
// _settings.push(["setEaveClientId", eaveClientId]);

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

function initEave(clientId) {
  _settings.push(["setEaveClientId", clientId]);
}