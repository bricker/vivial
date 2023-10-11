import { EaveEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js";
import { GPTRequestEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/gpt_request_event.js";
import { PubSub } from "@google-cloud/pubsub";
import { sharedConfig } from "./config.js";
import { AnalyticsAccount } from "./core-api/models/account.js";
import { Team } from "./core-api/models/team.js";
import { eaveLogger, LogContext } from "./logging.js";
import { JsonObject, UUID } from "./types.js";
import { redact } from "./util.js";

// document me

const EVENT_TOPIC_ID = "eave_event";
const GPT_EVENT_TOPIC_ID = "gpt_request_event";

export interface EaveEventFields {
  event_name: string;
  event_description?: string;
  event_source?: string;
  opaque_params?: JsonObject | string;
  eave_visitor_id?: UUID;
  eave_account?: AnalyticsAccount;
  eave_team?: Team;
  eave_team_id?: UUID;
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

/**
 * Logs an event to the PubSub topic specified by `EVENT_TOPIC_ID`.
 * The event is created using the provided `fields` and `ctx`.
 * If `fields.opaque_params` is a string, it is directly assigned to `event.opaque_params`.
 * If `fields.opaque_params` is undefined, `event.opaque_params` is also set to undefined.
 * Otherwise, `event.opaque_params` is set to the JSON stringified version of `fields.opaque_params`.
 * If `fields.eave_team` is provided, its ID and JSON stringified version are assigned to `event.eave_team_id` and `event.eave_team` respectively.
 * If `fields.eave_team` is not provided but `ctx` contains "eave_team", the same assignments are made after attempting to cast "eave_team" to a JsonObject.
 * Similar assignments are made for `fields.eave_account` and "eave_account" in `ctx`.
 * `event.opaque_eave_ctx` is set to the JSON stringified version of `ctx.attributes`.
 * `event.eave_request_id` is set to `ctx.eave_request_id`.
 * If `event.eave_account_id` and `event.eave_team_id` are not set, they are assigned from `ctx.eave_account_id` and `ctx.eave_team_id` respectively.
 * The event is then converted to JSON and encoded to a protobuf message.
 * If analytics are enabled, the event is published to the PubSub topic and a debug log is written.
 * If the event fails to publish, an exception log is written.
 * If analytics are not enabled, a warning log is written.
 * @param fields - The fields to be logged in the event.
 * @param ctx - The context in which the event is being logged.
 */
export async function logEvent(fields: EaveEventFields, ctx: LogContext) {
  const pubSubClient = new PubSub();

  // Get the topic metadata to learn about its schema.
  const topic = pubSubClient.topic(EVENT_TOPIC_ID);

  const event = EaveEvent.create({
    event_name: fields.event_name,
    event_description: fields.event_description,
    event_source: fields.event_source,
    eave_visitor_id: fields.eave_visitor_id,
    eave_env: sharedConfig.eaveEnv,
    event_time: new Date().toISOString(),
  });

  if (typeof fields.opaque_params === "string") {
    event.opaque_params = fields.opaque_params;
  } else if (fields.opaque_params === undefined) {
    event.opaque_params = undefined;
  } else {
    event.opaque_params = JSON.stringify(fields.opaque_params);
  }

  if (fields.eave_team) {
    event.eave_team_id = fields.eave_team.id;
    event.eave_team = JSON.stringify(fields.eave_team);
  } else if (ctx.get("eave_team")) {
    try {
      const sketchyEaveTeam = <JsonObject | undefined>ctx.get("eave_team");
      event.eave_team_id = <string>sketchyEaveTeam?.["id"];
      event.eave_team = JSON.stringify(sketchyEaveTeam);
    } catch (e: any) {
      eaveLogger.exception(e, ctx);
    }
  }

  if (fields.eave_account) {
    event.eave_account_id = fields.eave_account.id;
    event.eave_account = JSON.stringify(fields.eave_account);
  } else if (ctx.get("eave_account")) {
    try {
      const sketchyEaveAccount = <JsonObject | undefined>(
        ctx.get("eave_account")
      );
      event.eave_team_id = <string>sketchyEaveAccount?.["id"];
      event.eave_team = JSON.stringify(sketchyEaveAccount);
    } catch (e: any) {
      eaveLogger.exception(e, ctx);
    }
  }

  event.opaque_eave_ctx = JSON.stringify(ctx.attributes);
  event.eave_request_id = ctx.eave_request_id;

  if (!event.eave_account_id && ctx.eave_account_id) {
    event.eave_account_id = ctx.eave_account_id;
  }

  if (!event.eave_team_id && ctx.eave_team_id) {
    event.eave_team_id = ctx.eave_team_id;
  }

  const jsonEvent = <JsonObject>EaveEvent.toJSON(event);
  const protoMessage = EaveEvent.encode(event).finish();
  const redactedEvent = makeLogEvent(jsonEvent);

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, redactedEvent);

    try {
      const messageId = await topic.publishMessage({ data: protoMessage });
      eaveLogger.debug("Analytics event published", ctx, redactedEvent, {
        result: [messageId],
      });
    } catch (e: any) {
      eaveLogger.exception(e, redactedEvent, ctx);
    }
  } else {
    eaveLogger.warning("Analytics disabled", { event: jsonEvent }, ctx);
  }
}

/**
 * Logs a GPT request event to a PubSub topic. The event is created using the provided fields and the current time.
 * If a LogContext is provided, it is used to set the eave_request_id and eave_team_id of the event.
 * The event is then converted to JSON and encoded as a protobuf message.
 * If analytics are enabled, the event is published to the PubSub topic and a debug message is logged.
 * If the event fails to publish, an exception is logged.
 * If analytics are disabled, a warning is logged.
 *
 * @param fields - The fields to use when creating the GPT request event.
 * @param ctx - Optional. The context to use when logging the event.
 */
export async function logGptRequest(
  fields: GPTRequestEventFields,
  ctx?: LogContext,
) {
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
  const redactedEvent = makeLogEvent(jsonEvent);

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, redactedEvent);

    try {
      const messageId = await topic.publishMessage({ data: protoMessage });
      eaveLogger.debug("Analytics event published", ctx, redactedEvent, {
        result: [messageId],
      });
    } catch (e: any) {
      eaveLogger.exception(e, redactedEvent, ctx);
    }
  } else {
    eaveLogger.warning("Analytics disabled", jsonEvent, ctx);
  }
}

/**
 * Transforms a JSON event object by adding a redacted version of the `opaque_params` field.
 * The redacted version will only show the first 100 characters of the `opaque_params` field.
 *
 * @param {JsonObject} jsonEvent - The JSON event object to transform.
 * @returns {JsonObject} The transformed JSON event object with a redacted `opaque_params` field.
 */
function makeLogEvent(jsonEvent: JsonObject): JsonObject {
  return {
    event: {
      ...jsonEvent,
      opaque_params: redact(jsonEvent["opaque_params"]?.toString(), 100),
    },
  };
}
