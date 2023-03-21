import crypto from 'crypto';
import { TemplateTag } from './types/TemplateTag';
import { TemplateTagContext } from './types/TemplateTagContext';

const SIGNATURE_PLACEHOLDER = '{{signature placeholder}}';
const ALGORITHM = 'sha256';
const ENCODING = 'hex';

function computeSignature(payload: string, key: string) {
  const hmac = crypto.createHmac(ALGORITHM, key);
  // FIXME: Add team_id
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
