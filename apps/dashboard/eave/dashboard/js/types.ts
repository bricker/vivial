export const eaveOrigin = "eave_dashboard";

export type VirtualEventField = {
  name: string;
  description?: string | null;
  field_type: string;
  mode: string | null;
  fields: VirtualEventField[] | null;
};

export type VirtualEventDetails = {
  id: string;
  view_id: string;
  readable_name: string;
  description?: string | null;
  fields?: VirtualEventField[] | null;
};

export type Team = {
  id: string;
  name: string;
  dashboard_access: boolean;
};

export type OnboardingSubmission = {
  platforms: string[];
  languages: string[];
  frameworks: string[];
  databases: string[];
  third_party_libs: string[];
};

export type ClientCredentials = {
  id: string;
  secret: string;
  description: string;
  combined: string;
  last_used?: string;
};

export type ListMyVirtualEventsResponseBody = {
  // This endpoint returns VirtualEventPeek[], but in the UI we keep a list of virtual events
  // and lazily populate the fields.
  // This endpoint will return Virtual Events _without_ fields.
  virtual_events: Array<VirtualEventDetails>;
};

export type GetMyVirtualEventDetailsResponseBody = {
  // This endpoint returns a single virtual event _with_ fields.
  virtual_event: VirtualEventDetails;
};

export type CreateMyOnboardingSubmissionRequestBody = {
  onboarding_submission: OnboardingSubmission;
};

export type CreateMyOnboardingSubmissionResponseBody = {
  onboarding_submission: OnboardingSubmission;
  team: Team;
};

export type GetMyOnboardingSubmissionResponseBody = {
  onboarding_submission?: OnboardingSubmission;
  team: Team;
};

export type GetMyClientCredentialsResponseBody = {
  client_credentials: ClientCredentials;
};

export type GetTeamResponseBody = {
  team: Team;
};

export type GlobalEaveWindow = Window &
  typeof globalThis & {
    eavedash: {
      apiBase?: string;
      embedBase?: string;
      assetBase?: string;
    };
  };

export type DashboardTeam = {
  id?: string;
  name?: string;
  dashboardAccess?: boolean;
  onboardingSubmission?: OnboardingSubmission;
  virtualEvents?: VirtualEventDetails[];
  clientCredentials?: ClientCredentials;
};

export type DashboardNetworkState = {
  teamIsLoading: boolean;
  teamIsErroring: boolean;
  teamRequestHasSucceededAtLeastOnce: boolean;
};

export type GlossaryNetworkState = {
  virtualEventsAreLoading: boolean;
  virtualEventsAreErroring: boolean;
};

export type OnboardingFormNetworkState = {
  // create request state
  formSubmitIsLoading: boolean;
  formSubmitIsErroring: boolean;
  // get request state
  formDataIsLoading: boolean;
  formDataIsErroring: boolean;
};

export type ClientCredentialsNetworkState = {
  credentialsAreLoading: boolean;
  credentialsAreErroring: boolean;
};

// The additional properties are set in the template header, so we know they exist.
export const eaveWindow: GlobalEaveWindow = window as GlobalEaveWindow;
