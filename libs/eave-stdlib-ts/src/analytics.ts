import { EaveEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js";
import { GPTRequestEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/gpt_request_event.js";
import { PubSub } from "@google-cloud/pubsub";
import { sharedConfig } from "./config.js";
import { eaveLogger, LogContext } from "./logging.js";
import { JsonObject } from "./types.js";

const EVENT_TOPIC_ID = "eave_event";
const GPT_EVENT_TOPIC_ID = "gpt_request_event";

export interface EaveEventFields {
  event_name: string;
  event_description?: string;
  event_source?: string;
  opaque_params?: string;
  eave_visitor_id?: string;
  eave_account?: string;
  eave_team?: string;
}

export interface GPTRequestEventFields {
  feature_name?: string;
  duration_seconds: number;
  input_cost_usd: number;
  output_cost_usd: number;
  input_prompt: string;
  output_response: string;
  input_token_count: number;
  output_token_count: number;
  model: string;
  document_id?: string;
}

export async function logEvent(fields: EaveEventFields, ctx?: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);

  const event = EaveEvent.create(fields);
  event.eave_env = sharedConfig.eaveEnv;
  event.event_time = new Date().toISOString();
  if (ctx !== undefined) {
    event.opaque_eave_ctx = JSON.stringify(ctx);
    event.eave_account_id = ctx.eave_account_id;
    event.eave_team_id = ctx.eave_team_id;
    event.eave_request_id = ctx.eave_request_id;
  }

  const jsonEvent = <JsonObject>EaveEvent.toJSON(event);
  const protoMessage = EaveEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, { pubsub: { event: jsonEvent } });
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug("Analytics event published", ctx, { pubsub: { event: jsonEvent, result: [messageId] } });
  } else {
    eaveLogger.warning("Analytics disabled", { event: jsonEvent }, ctx);
  }
}

export async function logGptRequest(fields: GPTRequestEventFields, ctx?: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(GPT_EVENT_TOPIC_ID);

  const event = GPTRequestEvent.create(fields);
  event.event_time = new Date().toISOString();
  if (ctx !== undefined) {
    event.eave_request_id = ctx.eave_request_id;
    event.eave_team_id = ctx.eave_team_id;
  }

  const jsonEvent = <JsonObject>GPTRequestEvent.toJSON(event);
  const protoMessage = GPTRequestEvent.encode(event).finish();

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, { pubsub: { event: jsonEvent } });
    const messageId = await topic.publishMessage({ data: protoMessage });
    eaveLogger.debug("Analytics event published", ctx, { pubsub: { event: jsonEvent, result: [messageId] } });
  } else {
    eaveLogger.warning("Analytics disabled", { event: jsonEvent }, ctx);
  }
}
