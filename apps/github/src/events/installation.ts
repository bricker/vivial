import { InstallationEvent } from '@octokit/webhooks-types';
import eaveLogger from '@eave-fyi/eave-stdlib-ts/src/logging.js';
import { logEvent } from '@eave-fyi/eave-stdlib-ts/src/analytics.js';
import { GitHubOperationsContext } from '../types.js';

/**
 * Receives github webhook installation events.
 * https://docs.github.com/en/webhooks-and-events/webhooks/webhook-events-and-payloads#push
 *
 * Only logs analytics events.
 */
export default async function handler(event: InstallationEvent, context: GitHubOperationsContext) {
  const { ctx } = context;
  eaveLogger.debug('Processing installation', ctx);

  switch (event.action) {
    case 'created':
      await logEvent({
        event_name: 'eave_github_app_installed',
        event_description: 'Eave GitHub App was installed by a GitHub user/org',
        event_source: 'installation github webhook event',
        opaque_params: JSON.stringify({
          app_id: event.installation.app_id,
        }),
      }, ctx);
      break;
    case 'unsuspend':
      await logEvent({
        event_name: 'eave_github_app_unsuspended',
        event_description: 'Eave GitHub App had access unsuspended by a GitHub user/org',
        event_source: 'installation github webhook event',
        opaque_params: JSON.stringify({
          app_id: event.installation.app_id,
        }),
      }, ctx);
      break;
    case 'deleted':
      await logEvent({
        event_name: 'eave_github_app_uninstalled',
        event_description: 'Eave GitHub App was uninstalled by a GitHub user/org',
        event_source: 'installation github webhook event',
        opaque_params: JSON.stringify({
          app_id: event.installation.app_id,
        }),
      }, ctx);
      break;
    case 'suspend':
      await logEvent({
        event_name: 'eave_github_app_suspended',
        event_description: 'Eave GitHub App was suspended by a GitHub user/org',
        event_source: 'installation github webhook event',
        opaque_params: JSON.stringify({
          app_id: event.installation.app_id,
        }),
      }, ctx);
      break;
    default: break;
  }
}