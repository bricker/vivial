import { CompactSign } from 'jose';
import { TemplateTag } from './types/TemplateTag';
import { TemplateTagContext } from './types/TemplateTagContext';

async function generateSignature(payload: string, encryptionKey: string): Promise<string> {
    const encoder = new TextEncoder();
    const encodedPayload = encoder.encode(payload);
    const encodedKey = encoder.encode(encryptionKey);
    const compactSign = new CompactSign(encodedPayload);
    const jws = await compactSign
        .setProtectedHeader({ alg: 'HS256' })
        .sign(encodedKey);
    return jws;
}

const signatureTag: TemplateTag = {
    name: 'hs265',
    displayName: 'HS256 Signature',
    description: 'An encrypted signature of the request body using the HS256 algorithm and an encryption key',
    args: [
        {
            defaultValue: '',
            description: 'The encryption key',
            displayName: 'Encryption Key',
            placeholder: '',
            type: 'string',
        },
    ],
    async run(templateTagContext: TemplateTagContext, encryptionKey: string): Promise<string> {
        const { request } = templateTagContext;
        const textBody = request.getBody().text;
        if (textBody === undefined) {
            return '';
        }
        const signature = await generateSignature(textBody, encryptionKey);
        return signature;
    },
};

export const templateTags = [signatureTag];
