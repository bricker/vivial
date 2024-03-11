export enum AuthProvider {
  google = "google",
}

export type AuthenticatedAccount = {
  id: string;
  auth_provider: AuthProvider;
  visitor_id: string | null;
  team_id: string;
  opaque_utm_params: { [key: string]: any } | null;
  email: string | null;
};

export type AnalyticsAccount = {
  id: string;
  auth_provider: AuthProvider;
  visitor_id: string | null;
  team_id: string;
  opaque_utm_params: { [key: string]: any } | null;
};
