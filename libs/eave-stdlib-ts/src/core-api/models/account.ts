export enum AuthProvider {
  google = "google",
  slack = "slack",
  atlassian = "atlassian",
}

export type AuthenticatedAccount = {
  id: string;
  auth_provider: AuthProvider;
  visitor_id: string | null;
  team_id: string;
  opaque_utm_params: {[key:string]: any} | null;
  email: string | null;
  access_token: string;
};

export type AnalyticsAccount = {
  id: string;
  auth_provider: AuthProvider;
  visitor_id: string | null;
  team_id: string;
  opaque_utm_params: {[key:string]: any} | null;
};
