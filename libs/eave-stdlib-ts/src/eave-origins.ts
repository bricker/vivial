import { InvalidEnumCase } from "./exceptions.js";

export enum EaveApp {
  eave_api = "eave_api",
  eave_www = "eave_www",
  eave_github_app = "eave_github_app",
  eave_slack_app = "eave_slack_app",
  eave_atlassian_app = "eave_atlassian_app",
  eave_jira_app = "eave_jira_app",
  eave_confluence_app = "eave_confluence_app",
}

export function appengineServiceName(eaveApp: EaveApp): string {
  switch (eaveApp) {
    case EaveApp.eave_api: return "api";
    case EaveApp.eave_www: return "www";
    case EaveApp.eave_github_app: return "github";
    case EaveApp.eave_slack_app: return "slack";
    case EaveApp.eave_atlassian_app: return "atlassian";
    case EaveApp.eave_jira_app: return "jira";
    case EaveApp.eave_confluence_app: return "confluence";
    default: throw new InvalidEnumCase(eaveApp);
  }
}

export enum ExternalOrigin {
  github_api_client = "github_api_client",
}
