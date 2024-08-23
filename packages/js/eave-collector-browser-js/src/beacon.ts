import { isTrackingConsentRevoked } from "./consent";
import { TRACKER_URL } from "./internal/compile-config";
import {
  EAVE_TRACKING_CONSENT_GRANTED_EVENT_TYPE,
  EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE,
  VISIBILITY_CHANGE_EVENT_TYPE,
} from "./internal/js-events";
import { logger } from "./internal/logging";
import { getCorrelationContext } from "./properties/correlation-context";
import { getUserAgentProperties } from "./properties/device";
import { getCurrentPageProperties } from "./properties/page";
import {
  BrowserEventPayload,
  DeviceProperties,
  EpochTimeStampSeconds,
  JsonScalar,
  ScalarMap,
  TargetProperties,
} from "./types";
import { uuidv4 } from "./util/uuid";

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
    if (!window.EAVE_CLIENT_ID) {
      logger.warn("EAVE_CLIENT_ID is not set.");
      return;
    }
    // this.startAutoflush();
  }

  startAutoflush() {
    if (this.#timerId) {
      return;
    }

    if (isTrackingConsentRevoked()) {
      logger.debug("Tracking consent not given, queue won't autoflush.");
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
        this.#flushQueue();
        // this.startAutoflush();
        break;
      }

      case EAVE_TRACKING_CONSENT_REVOKED_EVENT_TYPE: {
        // this.stopAutoflush();
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
   * Builds a payload, filling in standard attributes like user agent and session info.
   */
  async buildPayload({
    action,
    timestamp,
    target,
    extra,
  }: {
    action: string;
    timestamp: EpochTimeStampSeconds;
    target: TargetProperties | null;
    extra?: ScalarMap<JsonScalar>;
  }): Promise<BrowserEventPayload> {
    const eventId = uuidv4();
    const deviceProperties = await this.#getDeviceProperties();
    const currentPageProperties = getCurrentPageProperties();
    const corrCtx = getCorrelationContext();

    const payload: BrowserEventPayload = {
      event_id: eventId,
      action,
      timestamp,
      target,
      device: deviceProperties,
      current_page: currentPageProperties,
      extra,
      corr_ctx: corrCtx,
    };

    return payload;
  }

  /**
   * Send or queue single event
   */
  queueEvent(payload: BrowserEventPayload) {
    if (isTrackingConsentRevoked()) {
      this.#queue.push(payload);
      logger.debug("Queued event", payload);
    } else {
      this.#sendBatch([payload]);
    }
  }

  /**
   * Send batch of events
   */
  #sendBatch(payloads: BrowserEventPayload[]) {
    if (isTrackingConsentRevoked()) {
      return;
    }

    if (payloads.length === 0) {
      return;
    }

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
      const clientId: string | undefined = window.EAVE_CLIENT_ID;

      logger.debug("Sending events", payloads);

      const success = navigator.sendBeacon(`${TRACKER_URL}?clientId=${clientId}`, blob);

      if (!success) {
        logger.warn("Failed to send analytics.");
        return;
      }
    } catch (e) {
      logger.error(e);
      return;
    }
  }

  /**
   * Flush the queue
   */
  #flushQueue() {
    if (this.#queue.length === 0) {
      return;
    }

    if (isTrackingConsentRevoked()) {
      return;
    }

    const payloads = this.#queue.popAll();
    this.#sendBatch(payloads);
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
