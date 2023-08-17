import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { GitHubOperationsContext } from '../types.js';
import pushHandler from './push.js';
import pullRequestHandler from './pull-request.js';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
declare type HandlerFunction = (event: EmitterWebhookEvent<EmitterWebhookEventName> & any, context: GitHubOperationsContext) => Promise<void>;

type Registry = {
  [key: string]: HandlerFunction,
}

export default <Registry> {
  push: pushHandler.bind(null),
  'pull_request.closed': pullRequestHandler.bind(null),
};
