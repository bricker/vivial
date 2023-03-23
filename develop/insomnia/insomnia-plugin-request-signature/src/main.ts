import crypto from 'crypto';
import { TemplateTag } from './types/TemplateTag';
import { TemplateTagContext } from './types/TemplateTagContext';

const SIGNATURE_PLACEHOLDER = '{{signature placeholder}}';
const ALGORITHM = 'sha256';
const ENCODING = 'hex';

function computeSignature(payload: string, key: string) {
  const hmac = crypto.createHmac(ALGORITHM, key);
  hmac.update(payload);
  return hmac.digest(ENCODING);
}

// https://docs.insomnia.rest/insomnia/context-object-reference
export const signatureTemplateTag: TemplateTag = {
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
  async run(_: TemplateTagContext, key: string): Promise<string> {
    return `${SIGNATURE_PLACEHOLDER}:${key}`;
  }
};

export function signatureRequestHook(context: TemplateTagContext) {
  const textBody = context.request.getBody().text;
  console.log('[signatureRequestHook]', {textBody});
  if (textBody === undefined || textBody === null) {
    return;
  }

  const teamIdHeader = context.request.getHeaders().find((header) => {
    return header.name.toLowerCase() === 'eave-team-id';
  });

  const signatureHeader = context.request.getHeaders().find((header) => {
    return header.name.toLowerCase() === 'eave-signature';
  });

  if (signatureHeader === undefined) {
    console.log('[signatureRequestHook]', 'no eave-signature header');
    return;
  }

  const [_, key] = signatureHeader.value.split(':');
  if (key === undefined) {
    throw new Error('Key was not specified. The hmac template requires the key as an argument.');
  }

  const parts = [];
  if (teamIdHeader !== undefined) {
    console.log('[signatureRequestHook]', {teamIdHeader});
    parts.push(teamIdHeader.value);
  }

  parts.push(textBody);
  const signature = computeSignature(parts.join(''), key);
  console.log('[signatureRequestHook]', {signature});
  context.request.setHeader(signatureHeader.name, signature);
}
