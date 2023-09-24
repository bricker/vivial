import { AtlassianInstallation } from "./atlassian.js";
import { ConnectInstallation } from "./connect.js";
import { GithubInstallation } from "./github.js";
import { SlackInstallation } from "./slack.js";

/**
 * Key-value mapping of Integration to Installation info.
 * The keys here will match the enum cases in enums.Integration
 */
export type Integrations = {
  github_integration: GithubInstallation | null;
  slack_integration: SlackInstallation | null;
  atlassian_integration: AtlassianInstallation | null;
  confluence_integration: ConnectInstallation | null;
  jira_integration: ConnectInstallation | null;
};
