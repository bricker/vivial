import { isTrackingConsentRevoked } from "./consent";
import { TRACKER_URL } from "./internal/compile-config";
import { LOG_TAG } from "./internal/constants";
import {
  EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE,
  VISIBILITY_CHANGE_EVENT_TYPE,
} from "./internal/js-events";
import { getDiscoveryProperties } from "./properties/discovery";
import { getPageProperties } from "./properties/page";
import { getUserProperties } from "./properties/user";
import { getUserAgentProperties } from "./properties/device";
import { getSessionProperties } from "./session";
import { BrowserEventPayload, EpochTimeStampSeconds, JSONObject, KeyValueArray, TargetProperties, DeviceProperties } from "./types";

/**
 * A Queue with a maximum size.
 * If the user revoked tracking/cookie consent, then queueing events infinitely will unnecessarily use up browser resources.
 * The purpose of queueing requests is to capture events leading up to cookie consent, so only a few (maxsize) events are needed.
 */
class RequestQueue {
  #maxsize = 20;
  #overflow = 5;

  #queue: BrowserEventPayload[];

  constructor() {
    this.#queue = [];
  }

  get isFull(): boolean {
    return this.#queue.length >= this.#maxsize;
  }

  get length(): number {
    return this.#queue.length;
  }

  /**
   * Push a payload onto the queue.
   * If the queue size is higher than the maxsize + overflow, then the oldest payloads are removed.
   */
  push(...payloads: BrowserEventPayload[]) {
    this.#queue.unshift(...payloads);
    if (this.#queue.length > this.#maxsize + this.#overflow) {
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

  #memoDeviceProperties?: DeviceProperties;

  #timerId?: number;

  constructor() {
    this.#queue = new RequestQueue();

    // @ts-ignore: this is a known global variable implicitly set on the window.
    if (!EAVE_CLIENT_ID) { // eslint-disable-line no-undef
      console.warn(LOG_TAG, "EAVE_CLIENT_ID is not set.");
      return;
    }

    window.addEventListener(EAVE_COOKIE_CONSENT_GRANTED_EVENT_TYPE, this);
    document.addEventListener(VISIBILITY_CHANGE_EVENT_TYPE, this);
    this.startAutoflush();
  }

  startAutoflush() {
    if (this.#timerId) {
      return;
    }

    if (isTrackingConsentRevoked()) {
      console.debug(LOG_TAG, "Tracking consent not given, queue won't autoflush.");
      return;
    }

    this.#timerId = window.setInterval(() => {
      this.#flushQueue();
    }, 1000 * 5);
  }

  stopAutoflush() {
    if (this.#timerId !== undefined) {
      window.clearInterval(this.#timerId);
      this.#timerId = undefined;
    }
  }

  /**
   * Interface for EventTarget.dispatchEvent()
   */
  async handleEvent(event: Event) {
    switch (event.type) {
      case EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE: {
        this.startAutoflush();
        break;
      }

      case EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE: {
        this.stopAutoflush();
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
  async buildPayload({ action, timestamp, target, extra }: { action: string; timestamp: EpochTimeStampSeconds; target: TargetProperties | null; extra?: KeyValueArray }): Promise<BrowserEventPayload> {
    const deviceProperties = await this.#getDeviceProperties();
    const pageProperties = getPageProperties();
    const sessionProperties = getSessionProperties();
    const userProperties = getUserProperties();
    const discoveryProperties = getDiscoveryProperties();

    const payload: BrowserEventPayload = {
      action,
      timestamp,
      target,
      device: deviceProperties,
      page: pageProperties,
      session: sessionProperties,
      user: userProperties,
      discovery: discoveryProperties,
      extra,
    };

    return payload;
  }

  /**
   * Send single event
   */
  queueEvent(payload: BrowserEventPayload) {
    this.#queue.push(payload);
    console.debug(LOG_TAG, "Queued event", payload);

    if (this.#queue.isFull) {
      this.#flushQueue();
    }
  }

  /**
   * Send batch of events
   */
  #flushQueue() {
    if (this.#queue.length === 0) {
      return;
    }

    if (isTrackingConsentRevoked()) {
      return;
    }

    const payloads = this.#queue.popAll();

    try {
      const json = JSON.stringify({
        events: {
          browser_event: payloads,
        },
      });

      // Important note: The `type` property here should be `application/x-www-form-urlencoded`, because that mimetype is CORS-safelisted as documented here:
      // https://fetch.spec.whatwg.org/#cors-safelisted-request-header
      // If set to a non-safe mimetype (eg application/json), sendBeacon will send a pre-flight CORS request (OPTIONS) to the server, and the server is then responsible
      // for responding with CORS "access-control-allow-*" headers. That's okay, but it adds unnecessary overhead to both the client and the server.
      const blob = new Blob([json], {
        type: "application/x-www-form-urlencoded; charset=UTF-8",
      });

      // @ts-ignore: this is a known global variable implicitly set on the window.
      const clientId: string | undefined = EAVE_CLIENT_ID; // eslint-disable-line no-undef

      console.debug(LOG_TAG, "Sending events", payloads);

      const success = navigator.sendBeacon(`${TRACKER_URL}?clientId=${clientId}`, blob);

      if (!success) {
        console.warn(LOG_TAG, "failed to send analytics.");
        return;
      }
      // returns true if the user agent is able to successfully queue the data for transfer,
      // Otherwise it returns false and we need to try the regular way
    } catch (e) {
      console.error(LOG_TAG, e);
      return;
    }
  }

  async #getDeviceProperties(): Promise<DeviceProperties> {
    if (this.#memoDeviceProperties !== undefined) {
      return this.#memoDeviceProperties;
    }

    const properties = await getUserAgentProperties();
    this.#memoDeviceProperties = properties;
    return properties;
  }
}

export const requestManager = new RequestManager();
