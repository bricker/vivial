export enum AtlassianProduct {
  jira = "jira",
  confluence = "confluence",
}

export type ConnectInstallation = {
  id: string;
  product: AtlassianProduct;
  client_key: string;
  base_url: string;
  shared_secret: string;
  team_id?: string;
  atlassian_actor_account_id?: string;
  display_url?: string;
  description?: string;
};

export type RegisterConnectInstallationInput = {
  product: AtlassianProduct;
  client_key: string;
  base_url: string;
  shared_secret: string;
  atlassian_actor_account_id?: string;
  display_url?: string;
  description?: string;
};

export type QueryConnectInstallationInput = {
  product: AtlassianProduct;
  client_key?: string;
  team_id?: string;
};
