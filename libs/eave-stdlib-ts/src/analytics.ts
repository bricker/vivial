import { PubSub, Encodings } from '@google-cloud/pubsub';
import * as schemas from '@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js';
import eaveLogger, { LogContext } from './logging.js';
import { sharedConfig } from './config.js';
import { JsonObject } from './types.js';

const EVENT_TOPIC_ID = 'eave_event_topic';
const pubSubClient = new PubSub();

export async function logEvent(event: schemas.EaveEvent, ctx?: LogContext) {
  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);
  const [topicMetadata] = await topic.getMetadata();
  const topicSchemaMetadata = topicMetadata.schemaSettings;

  if (!topicSchemaMetadata) {
    eaveLogger.error(`schema missing for ${EVENT_TOPIC_ID}`, ctx);
    return;
  }
  const schemaEncoding = topicSchemaMetadata.encoding;

  if (schemaEncoding !== Encodings.Binary) {
    throw new Error(`unsupported encoding: ${schemaEncoding}`);
  }

  // eslint-disable-next-line no-param-reassign
  event.eave_env = sharedConfig.eaveEnv;
  event.event_ts = new Date().getTime();

  const protoMessage = schemas.EaveEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug(`published message to pubsub ${messageId}`, ctx);
  } else {
    const serializedEvent = <JsonObject>schemas.EaveEvent.toJSON(event);
    eaveLogger.warning('Analytics disabled', { event: serializedEvent }, ctx);
  }
}
