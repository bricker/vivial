var documentAlias = document,
  navigatorAlias = navigator,
  screenAlias = screen,
  windowAlias = window;

// TODO: get rid of this, dictate enabled trackers in source rather than loading script
// asynchronous tracker (or proxy)
if (typeof _paq !== "object") {
  var _paq = [];
}

global.ev = {
  expireDateTime: undefined,
  _paq,
  /* plugins */
  plugins: {},
  eventHandlers: {},
  /* alias frequently used globals for added minification */
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
