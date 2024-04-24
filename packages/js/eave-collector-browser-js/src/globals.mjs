// have to do this check on browser globals to make Node.js env happy
var documentAlias = typeof document !== "undefined" ? document : {},
  navigatorAlias = typeof navigator !== "undefined" ? navigator : {},
  screenAlias = typeof screen !== "undefined" ? screen : {},
  windowAlias = typeof window !== "undefined" ? window : {};

// use existing _paq settings if available
var _paq = typeof _paq !== "undefined" ? _paq : [];
_paq.push(["setTrackingCookies"])
_paq.push(["trackPageView"]);
_paq.push(["enableLinkTracking"]);
_paq.push(["enableRouteHistoryTracking"]);
_paq.push(["enableButtonClickTracking"]);
// TODO: update to point to eave backend
// TODO: switch on env whether to send to prod or stage
_paq.push(["setTrackerUrl", "http://localhost:3000/matomo"]);
// _paq.push(['setSiteId', '1']); // TODO: this isnt necessary

globalThis.eave = {
  expireDateTime: undefined,
  _paq,
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
