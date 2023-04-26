import crypto from 'crypto';
import { sharedConfig } from '../config';
export async function computeSignature(payload: string, teamId?: string): Promise<string> {
  const key = await sharedConfig.eaveSigningSecret;
  const hmac = crypto.createHmac('sha256', key);

  if (teamId !== undefined) {
    hmac.update(teamId);
  }

  hmac.update(payload);
  return hmac.digest('hex');
}
