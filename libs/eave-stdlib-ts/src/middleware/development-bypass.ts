import * as os from 'os';
import { constants as httpConstants } from 'node:http2';
import { Request, Response } from 'express';
import eaveLogger, { LogContext } from '../logging.js';
import { sharedConfig } from '../config.js';
import eaveHeaders from '../headers.js';

export function developmentBypassAllowed(req: Request, res: Response): boolean {
  if (!sharedConfig.devMode || sharedConfig.googleCloudProject === 'eave-production') {
    return false;
  }

  const devHeader = req.header(eaveHeaders.EAVE_DEV_BYPASS_HEADER);
  if (devHeader === undefined) {
    return false;
  }

  const ctx = LogContext.load(res);
  const expectedDevHeader = createDevHeaderValue();
  if (devHeader === expectedDevHeader) {
    eaveLogger.warning('Development bypass request accepted; some checks will be bypassed.', ctx);
    return true;
  }
  throw new Error(`Provided dev bypass header was not accepted. Expected: ${expectedDevHeader}`);
}

export function developmentBypassAuth(req: Request, res: Response): void {
  const ctx = LogContext.load(res);
  eaveLogger.warning('Bypassing auth verification in dev env', ctx);

  const accountId = req.header(httpConstants.HTTP2_HEADER_AUTHORIZATION);
  if (accountId === undefined || typeof accountId !== 'string') {
    throw new Error('Authorization header was empty');
  }

  // no account lookup since we cant access orm from ts...

  ctx.eave_account_id = accountId;
}

/**
 * Creates a string to replicate the value of Python's `os.uname()`
 */
function createDevHeaderValue(): string {
  return `posix.uname_result(sysname='${os.type()}', nodename='${os.hostname()}', release='${os.release()}', version='${os.version()}', machine='${os.machine()}')`;
}
