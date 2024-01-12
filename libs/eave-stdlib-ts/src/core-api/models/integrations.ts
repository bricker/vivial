import { AtlassianInstallationPeek } from "./atlassian.js";
import { ConnectInstallationPeek } from "./connect.js";
import { GithubInstallationPeek } from "./github.js";
import { SlackInstallationPeek } from "./slack.js";

/**
 * Key-value mapping of Integration to Installation info.
 * The keys here will match the enum cases in enums.Integration
 */
export type Integrations = {
  github_integration: GithubInstallationPeek | null;
  slack_integration: SlackInstallationPeek | null;
  atlassian_integration: AtlassianInstallationPeek | null;
  confluence_integration: ConnectInstallationPeek | null;
  jira_integration: ConnectInstallationPeek | null;
};
