import { EmitterWebhookEvent, EmitterWebhookEventName } from '@octokit/webhooks';
import { GitHubOperationsContext } from '../types.js';
import pushHandler from './push.js';
import pullRequestClosedHandler from './pull-request-closed.js';
import installationRepoAddedHandler from './installation-repositories-added.js';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type HandlerFunction = (event: EmitterWebhookEvent<EmitterWebhookEventName> & any, context: GitHubOperationsContext) => Promise<void>;

type Registry = {
  [key: string]: HandlerFunction,
}

export default <Registry> {
  push: pushHandler.bind(null),
  'pull_request.closed': pullRequestClosedHandler.bind(null),
  'installation_repositories.added': installationRepoAddedHandler.bind(null),
};
