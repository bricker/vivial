import * as os from 'os';
import { Request } from 'express';
import eaveLogger from '../logging';
import { sharedConfig } from '../config';
import eaveHeaders from '../headers';
import { EaveRequestState } from '../lib/request-state';

export function developmentBypassAllowed(req: Request): boolean {
  if (!sharedConfig.devMode || sharedConfig.googleCloudProject === 'eave-production') {
    return false;
  }

  const devHeader = req.header(eaveHeaders.EAVE_DEV_BYPASS_HEADER);
  if (devHeader === undefined) {
    return false;
  }

  const expectedDevHeader = createDevHeaderValue();
  if (devHeader === expectedDevHeader) {
    eaveLogger.warning('Development bypass request accepted; some checks will be bypassed.');
    return true;
  }
  throw new Error(`Provided dev bypass header was not accepted. Expected: ${expectedDevHeader}`);
}

export function developmentBypassAuth(req: Request, eaveState: EaveRequestState): void {
  eaveLogger.warning('Bypassing auth verification in dev env');

  const accountId = req.header(eaveHeaders.EAVE_AUTHORIZATION_HEADER);
  if (accountId === undefined || typeof accountId !== 'string') {
    throw new Error('Authorization header was empty');
  }

  // no account lookup since we cant access orm from ts...

  eaveState.eave_account_id = accountId; // eslint-disable-line
}

/**
 * Creates a string to replicate the value of Python's `os.uname()`
 */
function createDevHeaderValue(): string {
  return `posix.uname_result(sysname='${os.type()}', nodename='${os.hostname()}', release='${os.release()}', version='${os.version()}', machine='${os.machine()}')`;
}
