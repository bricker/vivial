import { CtxArg, ExpressHandlerArgs } from '@eave-fyi/eave-stdlib-ts/src/requests.js';
import { LogContext } from '@eave-fyi/eave-stdlib-ts/src/logging.js';

export default async function someEndpoint({ req, res }: ExpressHandlerArgs) {
  const ctx = LogContext.load(res);
  res.json({status: 'ok'});
}
