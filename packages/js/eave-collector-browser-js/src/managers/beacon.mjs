// @ts-check

import * as Types from "../types.mjs"; // eslint-disable-line no-unused-vars
import { cookieManager } from "./cookies.mjs";
import { consentManager } from "./consent.mjs";
import { sessionManager } from "./session.mjs";
import { eaveLogger } from "../internal/logging.mjs";
import { COOKIE_CONSENT_GRANTED_EVENT_TYPE, TRACKING_CONSENT_GRANTED_EVENT_TYPE, VISIBILITY_CHANGE_EVENT_TYPE } from "../internal/event-types.mjs";
import { TRACKER_URL } from "../internal/compile-config.mjs";
import { castPerformanceEntryToNavigationTiming } from "../util/typechecking.mjs";

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

    // @ts-ignore
    if (navigator.userAgentData?.getHighEntropyValues === undefined) {
      // navigator.userAgentData is not widely supported.
      // Additionally, it is only available in secure contexts (https).
      eaveLogger.warn("navigator.userAgentData not supported. Some user agent fields will be missing.");
    }
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
      case TRACKING_CONSENT_GRANTED_EVENT_TYPE: {
        this.#flushQueue();
        break;
      }

      case VISIBILITY_CHANGE_EVENT_TYPE: {
        if (document.visibilityState === "hidden") {
          this.#flushQueue();
        }
        break;
      }

      default: {
        break;
      }
    }
  }

  /**
   * @param {object} args
   * @param {string} args.action
   * @param {Date} args.timestamp
   * @param {Map<string, string>} [args.extra]
   *
   * @returns {Promise<Types.BrowserEventPayload>}
   */
  async buildPayload({ action, timestamp, extra }) {
    const clientProperties = await this.#getClientProperties();
    const performanceProperties = this.#getPerformanceProperties();
    const userProperties = this.#getUserProperties();
    const sessionProperties = this.#getSessionProperties();
    const pageProperties = this.#getPageProperties();

    const /** @type {Types.BrowserEventPayload} */ payload = {
      action,
      timestamp: timestamp.getTime() / 1000,
      extra,
      ...pageProperties,
      ...clientProperties,
      ...performanceProperties,
      ...userProperties,
      ...sessionProperties,
    };

    // add eave cookie context data
    for (const [cookieName, cookieValue] of cookieManager.getEaveCookies()) {
      payload[cookieName] = cookieValue;
    }

    return payload;
  }

  /**
   * @param {object} args
   * @param {Event} args.event
   * @param {Types.TargetProperties} args.target
   * @param {Date} args.timestamp
   * @param {Map<string, string>} [args.extra]
   *
   * @returns {Promise<Types.BrowserEventPayload>}
   */
  async buildPayloadFromEvent({ event, target, extra, timestamp }) {
    const payload = await this.buildPayload({
      action: event.type,
      timestamp,
    });

    payload.seconds_elapsed = event.timeStamp;

    payload
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
    if (consentManager.isTrackingConsentRevoked()) {
      this.#queue.push(...payloads);
      return;
    }

    try {
      const json = JSON.stringify({
        events: {
          browser_event: payloads,
        }
      });

      // Important note: The `type` property here should be `application/x-www-form-urlencoded`, because that mimetype is CORS-safelisted as documented here:
      // https://fetch.spec.whatwg.org/#cors-safelisted-request-header
      // If set to a non-safe mimetype (eg application/json), sendBeacon will send a pre-flight CORS request (OPTIONS) to the server, and the server is then responsible
      // for responding with CORS "access-control-allow-*" headers. That's okay, but it adds unnecessary overhead to both the client and the server.
      const blob = new Blob([json], {
        type: "application/x-www-form-urlencoded; charset=UTF-8",
      });

      /** @type {string | undefined} */
      // @ts-ignore - this is a known global variable implicitly set on the window.
      const clientId = EAVE_CLIENT_ID; // eslint-disable-line no-undef

      if (!clientId) {
        eaveLogger.warn("EAVE_CLIENT_ID is not set. Analytics is disabled.");
        return;
      }

      eaveLogger.debug("Sending events", payloads);

      const success = navigator.sendBeacon(`${TRACKER_URL}?clientId=${clientId}`, blob);

      if (!success) {
        eaveLogger.warn("failed to send analytics.");
        return;
      }
      // returns true if the user agent is able to successfully queue the data for transfer,
      // Otherwise it returns false and we need to try the regular way
    } catch (e) {
      eaveLogger.error(e);
      return;
    }
  }

  async #flushQueue() {
    const payloads = this.#queue.popAll();
    this.sendEventBatch(payloads);
  }

  /**
   * @returns {Types.PageProperties}
   */
  #getPageProperties() {
    const currentPageUrl = new URL(window.location.href);

    /** @type {Map<string, string[]>} */
    const current_query_params = new Map();
    currentPageUrl.searchParams.forEach((value, key) => {
      if (!current_query_params[key]) {
        current_query_params[key] = "ok";
      }
      current_query_params[key].push(value);
    });

    return {
      current_page_url: currentPageUrl.toString(),
      current_page_title: document.title,
      pageview_id: eave.pageViewId,
      current_query_params,
    }
  }

  /**
   * @returns {Types.SessionProperties}
   */
  #getSessionProperties() {
    return {
      session_id: sessionManager.getSessionId(),
      session_start_ms: sessionManager.getSessionStartMs(),
      session_duration_ms: sessionManager.getSessionDurationMs(),
    }
  }

  /**
   * @returns {Types.UserProperties}
   */
  #getUserProperties() {
    return {
      visitor_id: sessionManager.getVisitorId(),
      user_id: undefined, // FIXME
    }
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
      // navigator.userAgentData is not widely supported.
      // Additionally, it is only available in secure contexts (https).
      // A warning will have already been logged when this class was initialized. We don't warn here because it would spam the logs.
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
