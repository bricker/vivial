export type JiraInstallation = {
    id: string;
    client_key: string;
    base_url: string;
    team_id?: string;
    atlassian_actor_account_id?: string;
    shared_secret?: string;
    display_url?: string;
    description?: string;
}

export type RegisterJiraInstallationInput = {
    client_key: string;
    base_url: string;
    atlassian_actor_account_id?: string;
    shared_secret?: string;
    display_url?: string;
    description?: string;
}