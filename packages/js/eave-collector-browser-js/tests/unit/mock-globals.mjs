// mock browser globals for use in testing
const documentAlias = {};

const navigatorAlias = {};

const windowAlias = {};

const screenAlias = {};

global.eave = {
  expireDateTime: undefined,
  _paq: [],
  /* plugins */
  plugins: {},
  eventHandlers: {},
  /* alias frequently used globals for added minification */
  documentAlias,
  navigatorAlias,
  windowAlias,
  screenAlias,
  /* performance timing */
  performanceAlias: null,
  /* encode */
  encodeWrapper: encodeURIComponent,
  /* decode */
  decodeWrapper: decodeURIComponent,
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
