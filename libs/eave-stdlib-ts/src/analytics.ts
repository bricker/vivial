import { PubSub } from '@google-cloud/pubsub';
import { EaveEvent } from '@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js';
import { GPTRequestEvent } from '@eave-fyi/eave-pubsub-schemas/src/generated/gpt_request_event.js';
import eaveLogger, { LogContext } from './logging.js';
import { sharedConfig } from './config.js';
import { JsonObject } from './types.js';

const EVENT_TOPIC_ID = 'eave_event';
const GPT_EVENT_TOPIC_ID = 'gpt_request_event';

export async function logEvent(event: EaveEvent, ctx?: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);

  // eslint-disable-next-line no-param-reassign
  event.eave_env = sharedConfig.eaveEnv;
  event.event_time = new Date().toISOString();

  const jsonEvent = <JsonObject>EaveEvent.toJSON(event);
  const protoMessage = EaveEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug('Publishing analytics event', ctx, { pubsub: { event: jsonEvent } });
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug('Analytics event published', ctx, { pubsub: { event: jsonEvent, result: [messageId] } });
  } else {
    eaveLogger.warning('Analytics disabled', { event: jsonEvent }, ctx);
  }
}

export async function logGptRequest(event: GPTRequestEvent, ctx?: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(GPT_EVENT_TOPIC_ID);

  // eslint-disable-next-line no-param-reassign
  event.event_time = new Date().toISOString();

  const jsonEvent = <JsonObject>GPTRequestEvent.toJSON(event);
  const protoMessage = GPTRequestEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug('Publishing analytics event', ctx, { pubsub: { event: jsonEvent } });
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug('Analytics event published', ctx, { pubsub: { event: jsonEvent, result: [messageId] } });
  } else {
    eaveLogger.warning('Analytics disabled', { event: jsonEvent }, ctx);
  }
}
