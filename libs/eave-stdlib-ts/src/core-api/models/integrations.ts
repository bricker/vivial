import { AtlassianInstallation } from './atlassian.js';
import { GithubInstallation } from './github.js';
import { ConnectInstallation } from './connect.js';
import { SlackInstallation } from './slack.js';

/**
 * Key-value mapping of Integration to Installation info.
 * The keys here will match the enum cases in enums.Integration
 */
export type Integrations = {
  github_integration?: GithubInstallation;
  slack_integration?: SlackInstallation;
  atlassian_integration?: AtlassianInstallation;
  confluence_integration?: ConnectInstallation;
  jira_integration?: ConnectInstallation;
}
