// @ts-check

import * as Types from "../types.mjs"; // eslint-disable-line no-unused-vars
import { cookieManager } from "./cookies.mjs";
import { consentManager } from "./consent.mjs";
import { castPerformanceEntryToNavigationTiming, generateUniqueId, isFunction } from "../helpers.mjs";
import { sessionManager } from "./session.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { COOKIE_CONSENT_GRANTED_EVENT_TYPE, VISIBILITY_CHANGE_EVENT_TYPE } from "../internal/event-types.mjs";
import { clientId, eave } from "../main.mjs";

/**
 * A Queue with a maximum size.
 * If the user revoked tracking/cookie consent, then queueing events infinitely will unnecessarily use up browser resources.
 * The purpose of queueing requests is to capture events leading up to cookie consent, so only a few (maxsize) events are needed.
 */
class RequestQueue {
  #maxsize = 20;

  /** @type {Types.BrowserEventPayload[]} */
  #queue;

  constructor() {
    this.#queue = [];
  }

  /**
   * Push a payload onto the queue.
   * If the queue size is higher than the maxsize, then the oldest payloads are removed.
   *
   * @param {Types.BrowserEventPayload[]} payloads
   *
   * @noreturn
   */
  push(...payloads) {
    this.#queue.unshift(...payloads);
    if (this.#queue.length > this.#maxsize) {
      this.#queue.splice(this.#maxsize);
    }
  }

  /**
   * @returns {Types.BrowserEventPayload | undefined}
   */
  pop() {
    return this.#queue.pop();
  }

  /**
   * @returns {Types.BrowserEventPayload[]}
   */
  popAll() {
    const items = this.#queue;
    this.#queue = [];
    return items;
  }
}

// PRODUCTION is a custom webpack plugin defined in the webpack.config.cjs file as
// a boolean describing whether the script was compiled with mode=production
// @ts-ignore
const trackerUrl = PRODUCTION // eslint-disable-line no-undef
  ? "https://api.eave.dev/public/ingest/browser"
  : "http://api.eave.run:8080/public/ingest/browser";

class RequestManager {
  /** @type {RequestQueue} */
  #queue;

  /**
   * @type {Types.ClientProperties | undefined}
   */
  #memoClientProperties;

  constructor() {
    this.#queue = new RequestQueue();
    window.addEventListener(COOKIE_CONSENT_GRANTED_EVENT_TYPE, this);
    document.addEventListener(VISIBILITY_CHANGE_EVENT_TYPE, this);
  }

  /**
   * Interface for EventTarget.dispatchEvent()
   *
   * @param {Event} event
   *
   * @noreturn
   */
  handleEvent(event) {
    switch (event.type) {
      case COOKIE_CONSENT_GRANTED_EVENT_TYPE:
        this.#flushQueue();
        break;
      case VISIBILITY_CHANGE_EVENT_TYPE:
        if (document.visibilityState === "hidden") {
          this.#flushQueue();
        }
        break;
      default:
        break;
    }
  }

  /**
   * @param {object} args
   * @param {Event} args.event
   * @param {Types.TargetProperties} args.target
   * @param {Date} args.timestamp
   * @param {{[key:string]: string}} [args.extra]
   *
   * @returns {Promise<Types.BrowserEventPayload>}
   */
  async buildPayloadFromEvent({ event, target, extra, timestamp }) {
    const currentPageUrl = new URL(window.location.href);
    const /** @type {{[key:string]: string[]}} */ current_query_params = {};
    currentPageUrl.searchParams.forEach((value, key) => {
      if (!current_query_params[key]) {
        current_query_params[key] = [];
      }
      current_query_params[key].push(value);
    });

    const clientProperties = await this.#getClientProperties();
    const performanceProperties = this.#getPerformanceProperties();

    const /** @type {Types.BrowserEventPayload} */ payload = {
      action: event.type,
      timestamp: timestamp.getTime() / 1000,
      seconds_elapsed: event.timeStamp,
      current_page_url: currentPageUrl.toString(),
      current_page_title: document.title,
      pageview_id: eave.pageViewId,
      current_query_params,
      visitor_id: sessionManager.getVisitorId(),
      session_id: sessionManager.getSessionId(),
      session_start_ms: sessionManager.getSessionStartMs(),
      session_duration_ms: sessionManager.getSessionDurationMs(),
      extra,
      ...target,
      ...clientProperties,
      ...performanceProperties,
    };

    // add eave cookie context data
    for (const [cookieName, cookieValue] of cookieManager.getEaveCookies()) {
      payload[cookieName] = cookieValue;
    }

    return payload;
  }

  /**
   * Send single event
   *
   * @param {Types.BrowserEventPayload} payload
   *
   * @noreturn
   */
  async sendEvent(payload) {
    this.sendEventBatch([payload]);
  }

  /**
   * Send batch of events
   *
   * @param {Types.BrowserEventPayload[]} payloads
   *
   * @noreturn
   */
  async sendEventBatch(payloads) {
    if (consentManager.isCookieConsentRevoked()) {
      this.#queue.push(...payloads);
      return;
    }

    try {
      const json = JSON.stringify({
        events: {
          browser_event: payloads,
        }
      });

      const blob = new Blob([json], {
        type: "application/json; charset=UTF-8",
      });

      if (!clientId) {
        eaveLogger.warn("EAVE_CLIENT_ID is not set. Analytics is disabled.");
        return false;
      }

      eaveLogger.debug("Sending events", payloads);

      const success = navigator.sendBeacon(`${trackerUrl}?clientId=${clientId}`, blob);

      if (success) {
        return true;
      } else {
        eaveLogger.warn("failed to send analytics.");
        return false;
      }
      // returns true if the user agent is able to successfully queue the data for transfer,
      // Otherwise it returns false and we need to try the regular way
    } catch (e) {
      eaveLogger.error(e);
      return false;
    }
  }

  async #flushQueue() {
    const payloads = this.#queue.popAll();
    this.sendEventBatch(payloads);
  }

  /**
   * @returns {Promise<Types.ClientProperties>}
   */
  async #getClientProperties() {
    // Much of this function is ts-ignored because navigator.userAgentData does not have wide support.

    if (this.#memoClientProperties !== undefined) {
      return this.#memoClientProperties;
    }

    const /** @type {Types.ClientProperties} */ clientProperties = {
      useragent: navigator.userAgent,
      screen_width: screen.width,
      screen_height: screen.height,
    }

    // @ts-ignore
    if (navigator.userAgentData?.getHighEntropyValues === undefined) {
      eaveLogger.warn("navigator.userAgentData not supported. Some user agent fields will be missing.");
      return clientProperties;
    }

    // Initialize with low entropy values that are always available (when userAgentData is supported)
    // @ts-ignore
    clientProperties.ua_brands = navigator.userAgentData.brands;
    // @ts-ignore
    clientProperties.ua_platform = navigator.userAgentData.platform;
    // @ts-ignore
    clientProperties.ua_mobile = navigator.userAgentData.mobile;

    // try to gather high entropy values
    // currently this methods simply returns the requested values through a Promise
    // In later versions it might require a user permission
    // @ts-ignore
    const highEntropyValues = await navigator.userAgentData.getHighEntropyValues([
      "formFactor",
      "fullVersionList",
      "model",
      "platformVersion",
    ]);

    clientProperties.ua_form_factor = highEntropyValues.formFactor;
    clientProperties.ua_full_version_list = highEntropyValues.fullVersionList;
    clientProperties.ua_model = highEntropyValues.model;
    clientProperties.ua_platform_version = highEntropyValues.platformVersion;

    return clientProperties;
  }

  /**
   * @returns {Types.PerformanceProperties | undefined}
   */
  #getPerformanceProperties() {
    const /** @type {Types.PerformanceProperties} */ performanceProperties = {};

    const entries = performance.getEntriesByType("navigation");

    // For PerformanceNavigationTiming, only the current document is included, so there is only one entry.
    // https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming
    const entry = entries[0];
    if (!entry) {
      return;
    }

    const timing = castPerformanceEntryToNavigationTiming(entry);
    if (!timing) {
      return;
    }

    performanceProperties.perf_network_latency_ms = timing.responseEnd;
    performanceProperties.perf_dom_load_latency_ms = timing.domComplete;

    return performanceProperties;
  }
}

export const requestManager = new RequestManager();
