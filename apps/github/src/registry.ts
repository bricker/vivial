import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { GitHubOperationsContext } from './types.js';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare type HandlerFunction = (event: EmitterWebhookEvent<EmitterWebhookEventName> & any, context: GitHubOperationsContext) => Promise<void>;

const registry: { [key:string]: HandlerFunction } = {};

export function registerHandler(name: string, func: HandlerFunction) {
  registry[name] = func.bind(null);
  eaveLogger.debug(`Registered github event handler ${name}`);
}

export function getHandler(name: string): HandlerFunction | undefined {
  const handler: HandlerFunction | undefined = registry[name];
  return handler;
}
