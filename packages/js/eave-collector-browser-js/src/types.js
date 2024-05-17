// @ts-check
import { Tracker } from "./tracker.mjs";

/**
 * @typedef EaveConfiguration
 * @property {string} [eaveClientId]
 */

/**
 * @typedef EaveTrackerManager
 * @property {boolean} initialized
 * @property {(event: string, handler: function) => void} on
 * @property {(event: string, handler: function) => void} off
 * @property {(event: string, extraParameters?: object, context?: object) => void} trigger
 * @property {(pluginName: string, pluginObj: object) => void} addPlugin
 * @property {(eaveUrl?: string, siteId?: number) => Tracker} getTracker
 * @property {() => Tracker[]} getAsyncTrackers
 * @property {(eaveUrl: string, siteId: number) => Tracker} addTracker
 * @property {(eaveUrl?: string, siteId?: number) => Tracker} getAsyncTracker
 * @property {() => void} retryMissedPluginCalls
 */

/**
 * @typedef EaveDOMManager
 * @property {(element: HTMLElement, eventType: string, eventHandler: function, useCapture: boolean) => void} addEventListener
 * @property {(callback: function) => void} onLoad
 * @property {(callback: function) => void} onReady
 * @property {(node: HTMLElement) => boolean} isNodeVisible
 * @property {(node: HTMLElement) => boolean} isOrWasNodeVisible
 */

/**
 * @typedef GlobalEaveProperties
 * @property {number} [expireDateTime]
 * @property {string[][]} settings
 * @property {{[key: string]: any}} plugins
 * @property {{[key: string]: any}} [eventHandlers]
 * @property {any[]} asyncTrackers
 * @property {any[]} missedPluginTrackerCalls
 * @property {number} coreConsentCounter
 * @property {number} coreHeartBeatCounter
 * @property {number} trackerIdCounter
 * @property {boolean} isPageUnloading
 * @property {string} trackerInstallCheckNonce
 * @property {any[]} [trackerPluginAsyncInit]
 * @property {any} [tracker]
 * @property {() => void} [trackerAsyncInit]
 * @property {EaveTrackerManager} [eave]
 */

/**
 * @typedef {Window & EaveConfiguration & { eave: GlobalEaveProperties }} GlobalEaveWindow
 */

/**
 * @typedef RequestPayload
 * @property {string} [eaveClientId]
 * @property {number} [clientTs]
 * @property {string} [currentPageUrl]
 * @property {{[key:string]: string}} [currentQueryParams]
 * @property {string} [charSet]
 * @property {string} [consent]
 * @property {{[key:string]: string}} [browserFeatures]
 * @property {{[key:string]: string}} [uadata]
 * @property {string} [action]
 * @property {string} [target]
 * @property {string} [customData]
 *
 *
 * ... etc.
 */

/**
 * @typedef {(p: { payload: RequestPayload, trackerUrl: string, success: boolean }) => void} RequestCallback
 */

export const Types  = {};