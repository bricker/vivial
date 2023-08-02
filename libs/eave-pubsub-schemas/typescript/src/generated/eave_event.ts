/* eslint-disable */
import * as _m0 from "protobufjs/minimal";

export interface EaveEvent {
  event_name: string;
  event_time: string;
  event_description?: string | undefined;
  event_source?: string | undefined;
  opaque_params?: string | undefined;
  eave_account_id?: string | undefined;
  eave_visitor_id?: string | undefined;
  eave_team_id?: string | undefined;
  eave_env?: string | undefined;
  opaque_eave_ctx?: string | undefined;
  eave_account?: string | undefined;
  eave_team?: string | undefined;
}

function createBaseEaveEvent(): EaveEvent {
  return {
    event_name: "",
    event_time: "",
    event_description: undefined,
    event_source: undefined,
    opaque_params: undefined,
    eave_account_id: undefined,
    eave_visitor_id: undefined,
    eave_team_id: undefined,
    eave_env: undefined,
    opaque_eave_ctx: undefined,
    eave_account: undefined,
    eave_team: undefined,
  };
}

export const EaveEvent = {
  encode(message: EaveEvent, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.event_name !== "") {
      writer.uint32(10).string(message.event_name);
    }
    if (message.event_time !== "") {
      writer.uint32(26).string(message.event_time);
    }
    if (message.event_description !== undefined) {
      writer.uint32(18).string(message.event_description);
    }
    if (message.event_source !== undefined) {
      writer.uint32(34).string(message.event_source);
    }
    if (message.opaque_params !== undefined) {
      writer.uint32(42).string(message.opaque_params);
    }
    if (message.eave_account_id !== undefined) {
      writer.uint32(50).string(message.eave_account_id);
    }
    if (message.eave_visitor_id !== undefined) {
      writer.uint32(58).string(message.eave_visitor_id);
    }
    if (message.eave_team_id !== undefined) {
      writer.uint32(66).string(message.eave_team_id);
    }
    if (message.eave_env !== undefined) {
      writer.uint32(74).string(message.eave_env);
    }
    if (message.opaque_eave_ctx !== undefined) {
      writer.uint32(82).string(message.opaque_eave_ctx);
    }
    if (message.eave_account !== undefined) {
      writer.uint32(90).string(message.eave_account);
    }
    if (message.eave_team !== undefined) {
      writer.uint32(98).string(message.eave_team);
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
        case 3:
          if (tag != 26) {
            break;
          }

          message.event_time = reader.string();
          continue;
        case 2:
          if (tag != 18) {
            break;
          }

          message.event_description = reader.string();
          continue;
        case 4:
          if (tag != 34) {
            break;
          }

          message.event_source = reader.string();
          continue;
        case 5:
          if (tag != 42) {
            break;
          }

          message.opaque_params = reader.string();
          continue;
        case 6:
          if (tag != 50) {
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
        case 11:
          if (tag != 90) {
            break;
          }

          message.eave_account = reader.string();
          continue;
        case 12:
          if (tag != 98) {
            break;
          }

          message.eave_team = reader.string();
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
      event_time: isSet(object.event_time) ? String(object.event_time) : "",
      event_description: isSet(object.event_description) ? String(object.event_description) : undefined,
      event_source: isSet(object.event_source) ? String(object.event_source) : undefined,
      opaque_params: isSet(object.opaque_params) ? String(object.opaque_params) : undefined,
      eave_account_id: isSet(object.eave_account_id) ? String(object.eave_account_id) : undefined,
      eave_visitor_id: isSet(object.eave_visitor_id) ? String(object.eave_visitor_id) : undefined,
      eave_team_id: isSet(object.eave_team_id) ? String(object.eave_team_id) : undefined,
      eave_env: isSet(object.eave_env) ? String(object.eave_env) : undefined,
      opaque_eave_ctx: isSet(object.opaque_eave_ctx) ? String(object.opaque_eave_ctx) : undefined,
      eave_account: isSet(object.eave_account) ? String(object.eave_account) : undefined,
      eave_team: isSet(object.eave_team) ? String(object.eave_team) : undefined,
    };
  },

  toJSON(message: EaveEvent): unknown {
    const obj: any = {};
    message.event_name !== undefined && (obj.event_name = message.event_name);
    message.event_time !== undefined && (obj.event_time = message.event_time);
    message.event_description !== undefined && (obj.event_description = message.event_description);
    message.event_source !== undefined && (obj.event_source = message.event_source);
    message.opaque_params !== undefined && (obj.opaque_params = message.opaque_params);
    message.eave_account_id !== undefined && (obj.eave_account_id = message.eave_account_id);
    message.eave_visitor_id !== undefined && (obj.eave_visitor_id = message.eave_visitor_id);
    message.eave_team_id !== undefined && (obj.eave_team_id = message.eave_team_id);
    message.eave_env !== undefined && (obj.eave_env = message.eave_env);
    message.opaque_eave_ctx !== undefined && (obj.opaque_eave_ctx = message.opaque_eave_ctx);
    message.eave_account !== undefined && (obj.eave_account = message.eave_account);
    message.eave_team !== undefined && (obj.eave_team = message.eave_team);
    return obj;
  },

  create<I extends Exact<DeepPartial<EaveEvent>, I>>(base?: I): EaveEvent {
    return EaveEvent.fromPartial(base ?? {});
  },

  fromPartial<I extends Exact<DeepPartial<EaveEvent>, I>>(object: I): EaveEvent {
    const message = createBaseEaveEvent();
    message.event_name = object.event_name ?? "";
    message.event_time = object.event_time ?? "";
    message.event_description = object.event_description ?? undefined;
    message.event_source = object.event_source ?? undefined;
    message.opaque_params = object.opaque_params ?? undefined;
    message.eave_account_id = object.eave_account_id ?? undefined;
    message.eave_visitor_id = object.eave_visitor_id ?? undefined;
    message.eave_team_id = object.eave_team_id ?? undefined;
    message.eave_env = object.eave_env ?? undefined;
    message.opaque_eave_ctx = object.opaque_eave_ctx ?? undefined;
    message.eave_account = object.eave_account ?? undefined;
    message.eave_team = object.eave_team ?? undefined;
    return message;
  },
};

type Builtin = Date | Function | Uint8Array | string | number | boolean | undefined;

type DeepPartial<T> = T extends Builtin ? T
  : T extends Array<infer U> ? Array<DeepPartial<U>> : T extends ReadonlyArray<infer U> ? ReadonlyArray<DeepPartial<U>>
  : T extends {} ? { [K in keyof T]?: DeepPartial<T[K]> }
  : Partial<T>;

type KeysOfUnion<T> = T extends T ? keyof T : never;
type Exact<P, I extends P> = P extends Builtin ? P
  : P & { [K in keyof P]: Exact<P[K], I[K]> } & { [K in Exclude<keyof I, KeysOfUnion<P>>]: never };

function isSet(value: any): boolean {
  return value !== null && value !== undefined;
}
