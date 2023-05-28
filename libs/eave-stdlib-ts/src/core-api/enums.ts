export enum AuthProvider {
  google = 'google',
  slack = 'slack',
  atlassian = 'atlassian',
}

export enum DocumentPlatform {
  eave = 'eave',
  confluence = 'confluence',
  google_drive = 'google_drive',
}

export enum SubscriptionSourcePlatform {
  slack = 'slack',
  github = 'github',
  jira = 'jira',
}

export enum SubscriptionSourceEvent {
  slack_message = 'slack_message',
  github_file_change = 'github_file_change',
  jira_issue_comment = 'jira_issue_comment',
}

/**
 * Link types that we support fetching content from for integration into AI documentation creation.
 */
export enum LinkType {
  github = 'github',
}

export enum EaveForgeInboundOperation {
  createDocument = 'createDocument',
  updateDocument = 'updateDocument',
  archiveDocument = 'archiveDocument',

}
