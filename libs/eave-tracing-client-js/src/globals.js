var documentAlias = document,
  navigatorAlias = navigator,
  screenAlias = screen,
  windowAlias = window;

// TODO: get rid of this, dictate enabled trackers in source rather than loading script
// asynchronous tracker (or proxy)
if (typeof _paq !== "object") {
  var _paq = [];
  _paq.push(['trackPageView']);
  _paq.push(['enableLinkTracking']);
  _paq.push(['enableRouteHistoryTracking']);
  _paq.push(['enableButtonClickTracking']);
  // TODO: add eave team ID or something to correlate event w/ team
  // var u="http://localhost:3001/";
  _paq.push(['setTrackerUrl', 'http://localhost:3000/matomo']);
  _paq.push(['setSiteId', '1']);
}
console.log(_paq)

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
