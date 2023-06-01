export type JiraInstallation = {
    id: string;
    client_key: string;
    base_url: string;
    shared_secret: string;
    team_id?: string;
    atlassian_actor_account_id?: string;
    display_url?: string;
    description?: string;
}

export type RegisterJiraInstallationInput = {
    client_key: string;
    base_url: string;
    shared_secret: string;
    atlassian_actor_account_id?: string;
    display_url?: string;
    description?: string;
}

export type QueryJiraInstallationInput = {
    client_key: string;
}