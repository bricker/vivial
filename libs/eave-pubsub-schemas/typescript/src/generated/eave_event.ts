/* eslint-disable */
import * as _m0 from "protobufjs/minimal";

export interface EaveEvent {
  event_name: string;
  event_description: string;
  event_ts: number;
  event_source: string;
  opaque_params: string;
  eave_account_id: string;
  eave_visitor_id: string;
  eave_team_id: string;
  eave_env: string;
  opaque_eave_ctx: string;
}

function createBaseEaveEvent(): EaveEvent {
  return {
    event_name: "",
    event_description: "",
    event_ts: 0,
    event_source: "",
    opaque_params: "",
    eave_account_id: "",
    eave_visitor_id: "",
    eave_team_id: "",
    eave_env: "",
    opaque_eave_ctx: "",
  };
}

export const EaveEvent = {
  encode(message: EaveEvent, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.event_name !== "") {
      writer.uint32(10).string(message.event_name);
    }
    if (message.event_description !== "") {
      writer.uint32(18).string(message.event_description);
    }
    if (message.event_ts !== 0) {
      writer.uint32(45).float(message.event_ts);
    }
    if (message.event_source !== "") {
      writer.uint32(50).string(message.event_source);
    }
    if (message.opaque_params !== "") {
      writer.uint32(26).string(message.opaque_params);
    }
    if (message.eave_account_id !== "") {
      writer.uint32(34).string(message.eave_account_id);
    }
    if (message.eave_visitor_id !== "") {
      writer.uint32(58).string(message.eave_visitor_id);
    }
    if (message.eave_team_id !== "") {
      writer.uint32(66).string(message.eave_team_id);
    }
    if (message.eave_env !== "") {
      writer.uint32(74).string(message.eave_env);
    }
    if (message.opaque_eave_ctx !== "") {
      writer.uint32(82).string(message.opaque_eave_ctx);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): EaveEvent {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseEaveEvent();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag != 10) {
            break;
          }

          message.event_name = reader.string();
          continue;
        case 2:
          if (tag != 18) {
            break;
          }

          message.event_description = reader.string();
          continue;
        case 5:
          if (tag != 45) {
            break;
          }

          message.event_ts = reader.float();
          continue;
        case 6:
          if (tag != 50) {
            break;
          }

          message.event_source = reader.string();
          continue;
        case 3:
          if (tag != 26) {
            break;
          }

          message.opaque_params = reader.string();
          continue;
        case 4:
          if (tag != 34) {
            break;
          }

          message.eave_account_id = reader.string();
          continue;
        case 7:
          if (tag != 58) {
            break;
          }

          message.eave_visitor_id = reader.string();
          continue;
        case 8:
          if (tag != 66) {
            break;
          }

          message.eave_team_id = reader.string();
          continue;
        case 9:
          if (tag != 74) {
            break;
          }

          message.eave_env = reader.string();
          continue;
        case 10:
          if (tag != 82) {
            break;
          }

          message.opaque_eave_ctx = reader.string();
          continue;
      }
      if ((tag & 7) == 4 || tag == 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): EaveEvent {
    return {
      event_name: isSet(object.event_name) ? String(object.event_name) : "",
      event_description: isSet(object.event_description) ? String(object.event_description) : "",
      event_ts: isSet(object.event_ts) ? Number(object.event_ts) : 0,
      event_source: isSet(object.event_source) ? String(object.event_source) : "",
      opaque_params: isSet(object.opaque_params) ? String(object.opaque_params) : "",
      eave_account_id: isSet(object.eave_account_id) ? String(object.eave_account_id) : "",
      eave_visitor_id: isSet(object.eave_visitor_id) ? String(object.eave_visitor_id) : "",
      eave_team_id: isSet(object.eave_team_id) ? String(object.eave_team_id) : "",
      eave_env: isSet(object.eave_env) ? String(object.eave_env) : "",
      opaque_eave_ctx: isSet(object.opaque_eave_ctx) ? String(object.opaque_eave_ctx) : "",
    };
  },

  toJSON(message: EaveEvent): unknown {
    const obj: any = {};
    message.event_name !== undefined && (obj.event_name = message.event_name);
    message.event_description !== undefined && (obj.event_description = message.event_description);
    message.event_ts !== undefined && (obj.event_ts = message.event_ts);
    message.event_source !== undefined && (obj.event_source = message.event_source);
    message.opaque_params !== undefined && (obj.opaque_params = message.opaque_params);
    message.eave_account_id !== undefined && (obj.eave_account_id = message.eave_account_id);
    message.eave_visitor_id !== undefined && (obj.eave_visitor_id = message.eave_visitor_id);
    message.eave_team_id !== undefined && (obj.eave_team_id = message.eave_team_id);
    message.eave_env !== undefined && (obj.eave_env = message.eave_env);
    message.opaque_eave_ctx !== undefined && (obj.opaque_eave_ctx = message.opaque_eave_ctx);
    return obj;
  },
};

function isSet(value: any): boolean {
  return value !== null && value !== undefined;
}
