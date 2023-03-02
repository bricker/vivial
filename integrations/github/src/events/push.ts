import { PushEvent } from '@octokit/webhooks-types';
// import { GitHubOperationsContext } from '../types';

export default async function handler(event: PushEvent /* , context: GitHubOperationsContext */) {
  console.info('Processing push', event);
}
