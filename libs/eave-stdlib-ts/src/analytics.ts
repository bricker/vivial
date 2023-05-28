import { PubSub, Encodings } from '@google-cloud/pubsub';
import { EaveEvent } from '@eave-fyi/eave-pubsub-schemas/src/generated/eave_event';
import eaveLogger from './logging';

const EVENT_TOPIC_ID = 'eave_event_topic';
const pubSubClient = new PubSub();

export async function logEvent(event: EaveEvent) {
  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);
  const [topicMetadata] = await topic.getMetadata();
  const topicSchemaMetadata = topicMetadata.schemaSettings;

  if (!topicSchemaMetadata) {
    eaveLogger.error(`schema missing for ${EVENT_TOPIC_ID}`);
    return;
  }
  const schemaEncoding = topicSchemaMetadata.encoding;

  if (schemaEncoding !== Encodings.Binary) {
    throw new Error(`unsupported encoding: ${schemaEncoding}`);
  }

  const protoMessage = EaveEvent.encode(event).finish();
  const messageId = await topic.publishMessage({ data: protoMessage });
  eaveLogger.debug(`published message to pubsub ${messageId}`);
}
