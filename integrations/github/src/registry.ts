import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { GitHubOperationsContext } from './types';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare type HandlerFunction = (event: EmitterWebhookEvent<EmitterWebhookEventName> & any, context: GitHubOperationsContext) => Promise<void>;

const registry: { [key:string]: HandlerFunction } = {};

export function registerHandler(name: string, func: HandlerFunction) {
  registry[name] = func.bind(null);
  console.info('Registered github event handler', name);
}

export function getHandler(name: string): HandlerFunction | undefined {
  const handler: HandlerFunction | undefined = registry[name];
  return handler;
}
