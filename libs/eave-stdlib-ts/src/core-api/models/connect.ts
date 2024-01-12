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
  team_id: string | null;
  atlassian_actor_account_id: string | null;
  display_url: string | null;
  description: string | null;
};

export type ConnectInstallationPeek = {
  id: string;
  product: AtlassianProduct;
  base_url: string;
  org_url: string;
  team_id: string | null;
  display_url: string | null;
  description: string | null;
};

export type RegisterConnectInstallationInput = {
  product: AtlassianProduct;
  client_key: string;
  base_url: string;
  shared_secret: string;
  atlassian_actor_account_id: string | null;
  display_url: string | null;
  description: string | null;
};

export type QueryConnectInstallationInput = {
  product: AtlassianProduct;

  // TODO: Validation on these fields (see the Python counterpart for an example)
  client_key?: string;
  team_id?: string;
};
