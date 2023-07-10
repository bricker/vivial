import { PubSub } from '@google-cloud/pubsub';
import * as schemas from '@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js';
import eaveLogger, { LogContext } from './logging.js';
import { sharedConfig } from './config.js';
import { JsonObject } from './types.js';

const EVENT_TOPIC_ID = 'eave_event';

export async function logEvent(event: schemas.EaveEvent, ctx?: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);

  // eslint-disable-next-line no-param-reassign
  event.eave_env = sharedConfig.eaveEnv;
  event.event_time = new Date().toISOString();

  const jsonEvent = <JsonObject>schemas.EaveEvent.toJSON(event);
  const protoMessage = schemas.EaveEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug('Publishing analytics event', ctx, { pubsub: { event: jsonEvent } });
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug('Analytics event published', ctx, { pubsub: { event: jsonEvent, result: [messageId] } });
  } else {
    eaveLogger.warning('Analytics disabled', { event: jsonEvent }, ctx);
  }
}
