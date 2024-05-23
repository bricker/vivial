// @ts-check

/**
 * @typedef EaveConfiguration
 *
 * @property {string} [eaveClientId]
 */

/**
 * @typedef EaveDOMManager
 *
 * @property {(element: HTMLElement, eventType: string, eventHandler: function, useCapture: boolean) => void} addEventListener
 * @property {(callback: function) => void} onLoad
 * @property {(callback: function) => void} onReady
 * @property {(node: HTMLElement) => boolean} isNodeVisible
 * @property {(node: HTMLElement) => boolean} isOrWasNodeVisible
 */

/**
 * @typedef GlobalEaveProperties
 *
 * @property {string} pageViewId
 * @property {string} [clientId]
 */

/**
 * @typedef {Window & EaveConfiguration & { eave: GlobalEaveProperties }} GlobalEaveWindow
 */


/**
 * @typedef ClientProperties
 *
 * @property {number} screen_width
 * @property {number} screen_height
 * @property {string} useragent
 * @property {{brand: string, version: string}[]} [ua_brands]
 * @property {string} [ua_platform]
 * @property {boolean} [ua_mobile]
 * @property {string} [ua_form_factor]
 * @property {{brand: string, version: string}[]} [ua_full_version_list]
 * @property {string} [ua_model]
 * @property {string} [ua_platform_version]
 */

/**
 * @typedef PageProperties
 *
 * @property {string} current_page_url
 * @property {string} current_page_title
 * @property {string} pageview_id
 * @property {{[key:string]: string[]}} [current_query_params]
 */

/**
 * @typedef SessionProperties
 *
 * @property {string} [session_id]
 * @property {number} [session_start_ms]
 * @property {number} [session_duration_ms]
 */

/**
 * @typedef UserProperties
 *
 * @property {string} [visitor_id]
 * @property {string} [user_id]
 */

/**
 * @typedef TargetProperties
 *
 * @property {string} [target_type]
 * @property {string} [target_id]
 * @property {{[key:string]: string}} [target_attributes]
 */

/**
 * @typedef PerformanceProperties
 *
 * @property {number} [perf_network_latency_ms]
 * @property {number} [perf_dom_load_latency_ms]
 */

/**
 * @typedef EventProperties
 *
 * @property {string} action
 * @property {number} timestamp
 * @property {number} [seconds_elapsed]
 * @property {{[key:string]: string}} [extra]
 */

/**
 * @typedef {ClientProperties & PerformanceProperties & PageProperties & SessionProperties & UserProperties & TargetProperties & EventProperties} BrowserEventPayload
 */

/**
 * @typedef {(p: { payload: BrowserEventPayload, trackerUrl: string, success: boolean }) => void} RequestCallback
 */

export const Types  = {};