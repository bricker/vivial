import * as models from './models';

export type DocumentInput = {
  title: string;
  content: string;
  parent?: DocumentInput;
}

export type DocumentReferenceInput = {
  id: string;
}

export type SubscriptionInput = {
  source: models.SubscriptionSource;
}

export type TeamInput = {
  id: string;
}

export type SlackInstallationInput = {
  slack_team_id: string;
}

export type GithubInstallationInput = {
  github_install_id: string;
}

export namespace UpsertDocument {
  export type RequestBody = {
    document: DocumentInput;
    subscription: SubscriptionInput;
  }
  export type ResponseBody = {
    team: models.Team;
    subscription: models.Subscription;
    document_reference: models.DocumentReference;
  }
}

export namespace Status {
  export type ResponseBody = {
    service: string;
    version: string;
    status: string;
  }
}

export namespace CreateAccessRequest {
  export type RequestBody = {
    visitor_id?: string;
    email: string;
    opaque_input?: unknown;
  }
}

export namespace GetSubscription {
  export type RequestBody = {
    subscription: SubscriptionInput;
  }

  export type ResponseBody = {
    team: models.Team;
    subscription: models.Subscription;
    document_reference?: models.DocumentReference;
  }
}

export namespace CreateSubscription {
  export type RequestBody = {
    subscription: SubscriptionInput;
    document_reference?: DocumentReferenceInput;
  }

  export type ResponseBody = {
    team: models.Team;
    subscription: models.Subscription;
    document_reference?: models.DocumentReference;
  }
}

export namespace GetSlackInstallation {
  export type RequestBody = {
    slack_installation: SlackInstallationInput;
  }

  export type ResponseBody = {
    team: models.Team;
    slack_installation: models.SlackInstallation;
  }
}

export namespace GetGithubInstallation {
  export type RequestBody = {
    github_installation: GithubInstallationInput;
  }

  export type ResponseBody = {
    team: models.Team;
    github_installation: models.GithubInstallation;
  }
}

export namespace DeleteSubscription {
  export type RequestBody = {
    subscription: SubscriptionInput;
  }
}

export namespace GetTeam {
  export type ResponseBody = {
    team: models.Team;
    integrations: models.Integrations;
  }
}