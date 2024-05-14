/**
 *  @typedef {typeof globalThis & { eaveClientId?: string } & { _eave?: { expireDateTime?: string, settings: string[][], plugins?: {[key: string]: any}, eventHandlers?: {[key: string]: any}, asyncTrackers: any[], eave?: { getAsyncTrackers: () => any[] }, missedPluginTrackerCalls: any[], coreConsentCounter: number, coreHeartBeatCounter: number, trackerIdCounter: number, isPageUnloading: boolean, trackerInstallCheckNonce: string, trackerPluginAsyncInit?: any[], tracker?: any, trackerAsyncInit?: () => void } }} GlobalEaveWindow
 */

// export type GlobalEaveWindow = Window &
//   typeof globalThis & {
//     eaveClientId?: string;
//   } & {
//     eave: {
//       expireDateTime?: string;
//       settings: string[][];
//       /* plugins */
//       plugins?: {[key: string]: any};
//       eventHandlers?: {[key: string]: any};
//       /* asynchronous tracker */
//       asyncTrackers: any[];
//       /* local eave */
//       eave?: {
//         getAsyncTrackers: () => any[];
//       };
//       missedPluginTrackerCalls: any[];
//       coreConsentCounter: number;
//       coreHeartBeatCounter: number;
//       trackerIdCounter: number;
//       isPageUnloading: boolean;
//       trackerInstallCheckNonce: string;
//       trackerPluginAsyncInit?: any[];
//       tracker?: any;
//       trackerAsyncInit?: () => void;
//     };
//   };


// export const eaveWindow: GlobalEaveWindow = globalThis as GlobalEaveWindow;

export const Types  = {};