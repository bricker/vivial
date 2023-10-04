import { EaveEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/eave_event.js";
import { GPTRequestEvent } from "@eave-fyi/eave-pubsub-schemas/src/generated/gpt_request_event.js";
import { PubSub } from "@google-cloud/pubsub";
import { sharedConfig } from "./config.js";
import { AnalyticsAccount } from "./core-api/models/account.js";
import { Team } from "./core-api/models/team.js";
import { eaveLogger, LogContext } from "./logging.js";
import { JsonObject } from "./types.js";

const EVENT_TOPIC_ID = "eave_event";
const GPT_EVENT_TOPIC_ID = "gpt_request_event";

export interface EaveEventFields {
  event_name: string;
  event_description?: string;
  event_source?: string;
  opaque_params?: JsonObject | string;
  eave_visitor_id?: string;
  eave_account?: AnalyticsAccount;
  eave_team?: Team;
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
 * Asynchronously logs an event to the PubSub topic.
 * 
 * This function creates an EaveEvent object with the provided fields and context, 
 * then publishes the event to the PubSub topic if analytics are enabled. 
 * If analytics are disabled, a warning is logged instead.
 * 
 * @param {EaveEventFields} fields - The fields for the event to be logged.
 * @param {LogContext} ctx - The context for the event to be logged.
 * 
 * @throws {Error} If there is an error while publishing the event to the PubSub topic.
 * 
 * @returns {Promise<void>} A Promise that resolves when the event has been successfully logged.
 * 
 * @example
 * 
 * const fields = {
 *   event_name: 'test_event',
 *   event_description: 'This is a test event',
 *   event_source: 'test_source',
 *   eave_visitor_id: '12345',
 *   opaque_params: 'test_params',
 *   eave_team: { id: 'team1', name: 'Team 1' },
 *   eave_account: { id: 'account1', name: 'Account 1' }
 * };
 * 
 * const ctx = new LogContext();
 * 
 * logEvent(fields, ctx);
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

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, {
      pubsub: { event: jsonEvent },
    });

    try {
      const messageId = await topic.publishMessage({ data: protoMessage });
      eaveLogger.debug("Analytics event published", ctx, {
        pubsub: { event: jsonEvent, result: [messageId] },
      });
    } catch (e: any) {
      eaveLogger.exception(e, ctx);
    }
  } else {
    eaveLogger.warning("Analytics disabled", { event: jsonEvent }, ctx);
  }
}

/**
 * Asynchronously logs a GPT request event to a PubSub topic.
 *
 * @export
 * @async
 * @function logGptRequest
 * @param {GPTRequestEventFields} fields - The fields of the GPT request event to be logged.
 * @param {LogContext} [ctx] - The logging context, which may include request and team IDs.
 *
 * This function first creates a PubSub client and retrieves the metadata for the GPT event topic.
 * It then creates a GPT request event with the provided fields and the current time.
 * If a logging context is provided, the function adds the request and team IDs from the context to the event.
 *
 * The function then converts the event to JSON and encodes it as a protobuf message.
 * If analytics are enabled in the shared configuration, the function publishes the protobuf message to the PubSub topic and logs the event.
 * If the message publication fails, the function logs the exception.
 * If analytics are not enabled, the function logs a warning and the JSON event.
 *
 * @returns {Promise<void>} A promise that resolves when the logging operation is complete.
 * @throws {Error} If an error occurs while publishing the message to the PubSub topic.
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

  if (sharedConfig.analyticsEnabled) {
    eaveLogger.debug("Publishing analytics event", ctx, {
      pubsub: { event: jsonEvent },
    });

    try {
      const messageId = await topic.publishMessage({ data: protoMessage });
      eaveLogger.debug("Analytics event published", ctx, {
        pubsub: { event: jsonEvent, result: [messageId] },
      });
    } catch (e: any) {
      eaveLogger.exception(e, ctx);
    }
  } else {
    eaveLogger.warning("Analytics disabled", { event: jsonEvent }, ctx);
  }
}
