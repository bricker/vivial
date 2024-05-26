import { eaveLogger } from "./logging.js";
import { EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE, VISIBILITY_CHANGE_EVENT_TYPE } from "./internal/js-events.js";
import { TRACKER_URL } from "./internal/compile-config.js";
import { castPerformanceEntryToNavigationTiming } from "./util/typechecking.js";
import { getAllEaveCookies } from "./cookies.js";
import { isTrackingConsentRevoked } from "./consent.js";
import { getUserAgentProperties } from "./properties/user-agent.js";
import { BrowserEventPayload, EventProperties, JSONObject, PageProperties, PerformanceProperties, StringMap, UserAgentProperties } from "./types.js";
import { getPageProperties } from "./properties/page.js";
import { getUserProperties } from "./properties/user.js";
import { getPerformanceProperties } from "./properties/performance.js";
import { getSessionProperties } from "./session.js";
import { getDiscoveryProperties } from "./properties/discovery.js";

/**
 * A Queue with a maximum size.
 * If the user revoked tracking/cookie consent, then queueing events infinitely will unnecessarily use up browser resources.
 * The purpose of queueing requests is to capture events leading up to cookie consent, so only a few (maxsize) events are needed.
 */
class RequestQueue {
  #maxsize = 20;

  #queue: BrowserEventPayload[];

  constructor() {
    this.#queue = [];
  }

  /**
   * Push a payload onto the queue.
   * If the queue size is higher than the maxsize, then the oldest payloads are removed.
   */
  push(...payloads: BrowserEventPayload[]) {
    this.#queue.unshift(...payloads);
    if (this.#queue.length > this.#maxsize) {
      this.#queue.splice(this.#maxsize);
    }
  }

  pop(): BrowserEventPayload | undefined {
    return this.#queue.pop();
  }

  popAll(): BrowserEventPayload[] {
    const items = this.#queue;
    this.#queue = [];
    return items;
  }
}

class RequestManager {
  #queue: RequestQueue;

  #memoUserAgentProperties?: UserAgentProperties;

  constructor() {
    this.#queue = new RequestQueue();
    window.addEventListener(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, this);
    document.addEventListener(VISIBILITY_CHANGE_EVENT_TYPE, this);
  }

  /**
   * Interface for EventTarget.dispatchEvent()
   */
  async handleEvent(event: Event) {
    switch (event.type) {
      case EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE: {
        await this.#flushQueue();
        break;
      }

      case VISIBILITY_CHANGE_EVENT_TYPE: {
        if (document.visibilityState === "hidden") {
          await this.#flushQueue();
        }
        break;
      }

      default: {
        break;
      }
    }
  }

  /**
   * Builds a payload, filling in standard attributes like user agent and session info.
   */
  async buildPayload(
    { event, extra }:
    { event: EventProperties; extra?: JSONObject; }
  ): Promise<BrowserEventPayload> {
    const userAgentProperties = await this.#getUserAgentProperties();
    const performanceProperties = getPerformanceProperties();
    const pageProperties = getPageProperties();
    const sessionProperties = getSessionProperties();
    const userProperties = getUserProperties();
    const discoveryProperties = getDiscoveryProperties();
    const cookies = getAllEaveCookies();

    const payload: BrowserEventPayload = {
      user_agent: userAgentProperties,
      performance: performanceProperties,
      page: pageProperties,
      session: sessionProperties,
      user: userProperties,
      discovery: discoveryProperties,
      event,
      cookies,
      extra,
    };

    return payload;
  }

  /**
   * Send single event
   */
  queueEvent(payload: BrowserEventPayload) {
    this.queueEventBatch([payload]);
  }

  /**
   * Send batch of events
   */
  queueEventBatch(payloads: BrowserEventPayload[]) {
    if (isTrackingConsentRevoked()) {
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

      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore - this is a known global variable implicitly set on the window.
      const clientId: string | undefined = EAVE_CLIENT_ID; // eslint-disable-line no-undef

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

  #flushQueue() {
    const payloads = this.#queue.popAll();
    this.queueEventBatch(payloads);
  }

  async #getUserAgentProperties(): Promise<UserAgentProperties> {
    if (this.#memoUserAgentProperties !== undefined) {
      return this.#memoUserAgentProperties;
    }

    const properties = await getUserAgentProperties();
    this.#memoUserAgentProperties = properties;
    return properties;
  }
}

export const requestManager = new RequestManager();
