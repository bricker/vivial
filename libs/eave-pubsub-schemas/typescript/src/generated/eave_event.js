"use strict";
exports.__esModule = true;
exports.EaveEvent = void 0;
/* eslint-disable */
var _m0 = require("protobufjs/minimal");
function createBaseEaveEvent() {
    return {
        event_name: "",
        event_description: "",
        event_ts: 0,
        event_source: "",
        opaque_params: "",
        eave_account_id: "",
        eave_visitor_id: "",
        eave_team_id: ""
    };
}
exports.EaveEvent = {
    encode: function (message, writer) {
        if (writer === void 0) { writer = _m0.Writer.create(); }
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
        return writer;
    },
    decode: function (input, length) {
        var reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
        var end = length === undefined ? reader.len : reader.pos + length;
        var message = createBaseEaveEvent();
        while (reader.pos < end) {
            var tag = reader.uint32();
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
            }
            if ((tag & 7) == 4 || tag == 0) {
                break;
            }
            reader.skipType(tag & 7);
        }
        return message;
    },
    fromJSON: function (object) {
        return {
            event_name: isSet(object.event_name) ? String(object.event_name) : "",
            event_description: isSet(object.event_description) ? String(object.event_description) : "",
            event_ts: isSet(object.event_ts) ? Number(object.event_ts) : 0,
            event_source: isSet(object.event_source) ? String(object.event_source) : "",
            opaque_params: isSet(object.opaque_params) ? String(object.opaque_params) : "",
            eave_account_id: isSet(object.eave_account_id) ? String(object.eave_account_id) : "",
            eave_visitor_id: isSet(object.eave_visitor_id) ? String(object.eave_visitor_id) : "",
            eave_team_id: isSet(object.eave_team_id) ? String(object.eave_team_id) : ""
        };
    },
    toJSON: function (message) {
        var obj = {};
        message.event_name !== undefined && (obj.event_name = message.event_name);
        message.event_description !== undefined && (obj.event_description = message.event_description);
        message.event_ts !== undefined && (obj.event_ts = message.event_ts);
        message.event_source !== undefined && (obj.event_source = message.event_source);
        message.opaque_params !== undefined && (obj.opaque_params = message.opaque_params);
        message.eave_account_id !== undefined && (obj.eave_account_id = message.eave_account_id);
        message.eave_visitor_id !== undefined && (obj.eave_visitor_id = message.eave_visitor_id);
        message.eave_team_id !== undefined && (obj.eave_team_id = message.eave_team_id);
        return obj;
    }
};
function isSet(value) {
    return value !== null && value !== undefined;
}
