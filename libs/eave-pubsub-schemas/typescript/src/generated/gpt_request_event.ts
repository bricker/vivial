/* eslint-disable */
import Long from "long";
import _m0 from "protobufjs/minimal.js";

export interface GPTRequestEvent {
  feature_name?: string | undefined;
  event_time: string;
  duration_seconds: number;
  eave_request_id: string;
  input_cost_usd: number;
  output_cost_usd: number;
  input_prompt: string;
  output_response: string;
  input_token_count: number;
  output_token_count: number;
  model: string;
  eave_team_id?: string | undefined;
  document_id?: string | undefined;
}

function createBaseGPTRequestEvent(): GPTRequestEvent {
  return {
    feature_name: undefined,
    event_time: "",
    duration_seconds: 0,
    eave_request_id: "",
    input_cost_usd: 0,
    output_cost_usd: 0,
    input_prompt: "",
    output_response: "",
    input_token_count: 0,
    output_token_count: 0,
    model: "",
    eave_team_id: undefined,
    document_id: undefined,
  };
}

export const GPTRequestEvent = {
  encode(message: GPTRequestEvent, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.feature_name !== undefined) {
      writer.uint32(10).string(message.feature_name);
    }
    if (message.event_time !== "") {
      writer.uint32(18).string(message.event_time);
    }
    if (message.duration_seconds !== 0) {
      writer.uint32(24).int64(message.duration_seconds);
    }
    if (message.eave_request_id !== "") {
      writer.uint32(34).string(message.eave_request_id);
    }
    if (message.input_cost_usd !== 0) {
      writer.uint32(45).float(message.input_cost_usd);
    }
    if (message.output_cost_usd !== 0) {
      writer.uint32(53).float(message.output_cost_usd);
    }
    if (message.input_prompt !== "") {
      writer.uint32(58).string(message.input_prompt);
    }
    if (message.output_response !== "") {
      writer.uint32(66).string(message.output_response);
    }
    if (message.input_token_count !== 0) {
      writer.uint32(72).int64(message.input_token_count);
    }
    if (message.output_token_count !== 0) {
      writer.uint32(80).int64(message.output_token_count);
    }
    if (message.model !== "") {
      writer.uint32(90).string(message.model);
    }
    if (message.eave_team_id !== undefined) {
      writer.uint32(106).string(message.eave_team_id);
    }
    if (message.document_id !== undefined) {
      writer.uint32(114).string(message.document_id);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): GPTRequestEvent {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseGPTRequestEvent();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag != 10) {
            break;
          }

          message.feature_name = reader.string();
          continue;
        case 2:
          if (tag != 18) {
            break;
          }

          message.event_time = reader.string();
          continue;
        case 3:
          if (tag != 24) {
            break;
          }

          message.duration_seconds = longToNumber(reader.int64() as Long);
          continue;
        case 4:
          if (tag != 34) {
            break;
          }

          message.eave_request_id = reader.string();
          continue;
        case 5:
          if (tag != 45) {
            break;
          }

          message.input_cost_usd = reader.float();
          continue;
        case 6:
          if (tag != 53) {
            break;
          }

          message.output_cost_usd = reader.float();
          continue;
        case 7:
          if (tag != 58) {
            break;
          }

          message.input_prompt = reader.string();
          continue;
        case 8:
          if (tag != 66) {
            break;
          }

          message.output_response = reader.string();
          continue;
        case 9:
          if (tag != 72) {
            break;
          }

          message.input_token_count = longToNumber(reader.int64() as Long);
          continue;
        case 10:
          if (tag != 80) {
            break;
          }

          message.output_token_count = longToNumber(reader.int64() as Long);
          continue;
        case 11:
          if (tag != 90) {
            break;
          }

          message.model = reader.string();
          continue;
        case 13:
          if (tag != 106) {
            break;
          }

          message.eave_team_id = reader.string();
          continue;
        case 14:
          if (tag != 114) {
            break;
          }

          message.document_id = reader.string();
          continue;
      }
      if ((tag & 7) == 4 || tag == 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): GPTRequestEvent {
    return {
      feature_name: isSet(object.feature_name) ? String(object.feature_name) : undefined,
      event_time: isSet(object.event_time) ? String(object.event_time) : "",
      duration_seconds: isSet(object.duration_seconds) ? Number(object.duration_seconds) : 0,
      eave_request_id: isSet(object.eave_request_id) ? String(object.eave_request_id) : "",
      input_cost_usd: isSet(object.input_cost_usd) ? Number(object.input_cost_usd) : 0,
      output_cost_usd: isSet(object.output_cost_usd) ? Number(object.output_cost_usd) : 0,
      input_prompt: isSet(object.input_prompt) ? String(object.input_prompt) : "",
      output_response: isSet(object.output_response) ? String(object.output_response) : "",
      input_token_count: isSet(object.input_token_count) ? Number(object.input_token_count) : 0,
      output_token_count: isSet(object.output_token_count) ? Number(object.output_token_count) : 0,
      model: isSet(object.model) ? String(object.model) : "",
      eave_team_id: isSet(object.eave_team_id) ? String(object.eave_team_id) : undefined,
      document_id: isSet(object.document_id) ? String(object.document_id) : undefined,
    };
  },

  toJSON(message: GPTRequestEvent): unknown {
    const obj: any = {};
    message.feature_name !== undefined && (obj.feature_name = message.feature_name);
    message.event_time !== undefined && (obj.event_time = message.event_time);
    message.duration_seconds !== undefined && (obj.duration_seconds = Math.round(message.duration_seconds));
    message.eave_request_id !== undefined && (obj.eave_request_id = message.eave_request_id);
    message.input_cost_usd !== undefined && (obj.input_cost_usd = message.input_cost_usd);
    message.output_cost_usd !== undefined && (obj.output_cost_usd = message.output_cost_usd);
    message.input_prompt !== undefined && (obj.input_prompt = message.input_prompt);
    message.output_response !== undefined && (obj.output_response = message.output_response);
    message.input_token_count !== undefined && (obj.input_token_count = Math.round(message.input_token_count));
    message.output_token_count !== undefined && (obj.output_token_count = Math.round(message.output_token_count));
    message.model !== undefined && (obj.model = message.model);
    message.eave_team_id !== undefined && (obj.eave_team_id = message.eave_team_id);
    message.document_id !== undefined && (obj.document_id = message.document_id);
    return obj;
  },

  create<I extends Exact<DeepPartial<GPTRequestEvent>, I>>(base?: I): GPTRequestEvent {
    return GPTRequestEvent.fromPartial(base ?? {});
  },

  fromPartial<I extends Exact<DeepPartial<GPTRequestEvent>, I>>(object: I): GPTRequestEvent {
    const message = createBaseGPTRequestEvent();
    message.feature_name = object.feature_name ?? undefined;
    message.event_time = object.event_time ?? "";
    message.duration_seconds = object.duration_seconds ?? 0;
    message.eave_request_id = object.eave_request_id ?? "";
    message.input_cost_usd = object.input_cost_usd ?? 0;
    message.output_cost_usd = object.output_cost_usd ?? 0;
    message.input_prompt = object.input_prompt ?? "";
    message.output_response = object.output_response ?? "";
    message.input_token_count = object.input_token_count ?? 0;
    message.output_token_count = object.output_token_count ?? 0;
    message.model = object.model ?? "";
    message.eave_team_id = object.eave_team_id ?? undefined;
    message.document_id = object.document_id ?? undefined;
    return message;
  },
};

declare var self: any | undefined;
declare var window: any | undefined;
declare var global: any | undefined;
var tsProtoGlobalThis: any = (() => {
  if (typeof globalThis !== "undefined") {
    return globalThis;
  }
  if (typeof self !== "undefined") {
    return self;
  }
  if (typeof window !== "undefined") {
    return window;
  }
  if (typeof global !== "undefined") {
    return global;
  }
  throw "Unable to locate global object";
})();

type Builtin = Date | Function | Uint8Array | string | number | boolean | undefined;

type DeepPartial<T> = T extends Builtin ? T
  : T extends Array<infer U> ? Array<DeepPartial<U>> : T extends ReadonlyArray<infer U> ? ReadonlyArray<DeepPartial<U>>
  : T extends {} ? { [K in keyof T]?: DeepPartial<T[K]> }
  : Partial<T>;

type KeysOfUnion<T> = T extends T ? keyof T : never;
type Exact<P, I extends P> = P extends Builtin ? P
  : P & { [K in keyof P]: Exact<P[K], I[K]> } & { [K in Exclude<keyof I, KeysOfUnion<P>>]: never };

function longToNumber(long: Long): number {
  if (long.gt(Number.MAX_SAFE_INTEGER)) {
    throw new tsProtoGlobalThis.Error("Value is larger than Number.MAX_SAFE_INTEGER");
  }
  return long.toNumber();
}

// If you get a compile-error about 'Constructor<Long> and ... have no overlap',
// add '--ts_proto_opt=esModuleInterop=true' as a flag when calling 'protoc'.
if (_m0.util.Long !== Long) {
  _m0.util.Long = Long as any;
  _m0.configure();
}

function isSet(value: any): boolean {
  return value !== null && value !== undefined;
}
