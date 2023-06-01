import { AtlassianInstallation } from './atlassian.js';
import { ConfluenceInstallation } from './confluence.js';
import { ForgeInstallation } from './forge';
import { GithubInstallation } from './github.js';
import { JiraInstallation } from './jira.js';
import { SlackInstallation } from './slack.js';

/**
 * Key-value mapping of Integration to Installation info.
 * The keys here will match the enum cases in enums.Integration
 */
export type Integrations = {
  github_integration?: GithubInstallation;
  slack_integration?: SlackInstallation;
  atlassian_integration?: AtlassianInstallation;
  forge_integration?: ForgeInstallation;
  confluence_integration?: ConfluenceInstallation;
  jira_integration?: JiraInstallation;
}
