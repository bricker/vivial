// import crypto from 'crypto';
import { sharedConfig } from '../config.js';

// TODO: implement real signing!!
export async function computeSignature(_: string, __?: string): Promise<string> {
  const key = await sharedConfig.eaveGithubAppWebhookSecret;
  // const hmac = crypto.createHmac('sha256', key);

  // if (teamId !== undefined) {
  //   hmac.update(teamId);
  // }

  // hmac.update(payload);
  // return hmac.digest('hex');
  return key;
}
