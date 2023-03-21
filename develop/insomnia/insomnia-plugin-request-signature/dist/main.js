"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.signatureRequestHook = exports.signatureTemplateTag = void 0;
const crypto_1 = __importDefault(require("crypto"));
const SIGNATURE_PLACEHOLDER = '{{signature placeholder}}';
const ALGORITHM = 'sha256';
const ENCODING = 'hex';
function computeSignature(payload, key) {
    const hmac = crypto_1.default.createHmac(ALGORITHM, key);
    hmac.update(payload);
    return hmac.digest(ENCODING);
}
// https://docs.insomnia.rest/insomnia/context-object-reference
exports.signatureTemplateTag = {
    name: 'hmac_signature',
    displayName: 'HMAC Signature',
    description: 'HMAC Signature for the request. This can only be used in a header.',
    args: [
        {
            defaultValue: '',
            description: 'The encryption key to use when creating the signature',
            displayName: 'HMAC Encryption Key',
            placeholder: '',
            type: 'string',
        },
    ],
    async run(_, key) {
        return `${SIGNATURE_PLACEHOLDER}:${key}`;
    }
};
function signatureRequestHook(context) {
    const textBody = context.request.getBody().text;
    if (textBody === undefined) {
        throw new Error('Request body not present. Signature cannot be computed.');
    }
    context.request.getHeaders().forEach((header) => {
        if (header.value.indexOf(SIGNATURE_PLACEHOLDER) !== -1) {
            const [_, key] = header.value.split(':');
            if (key === undefined) {
                throw new Error('Key was not specified. The hmac template requires the key as an argument.');
            }
            const signature = computeSignature(textBody, key);
            header.value = signature;
        }
    });
}
exports.signatureRequestHook = signatureRequestHook;
//# sourceMappingURL=main.js.map