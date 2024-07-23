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

export type OnboardingSubmission = {
  response_data: object;
};

export type CreateMyOnboardingSubmissionRequestBody = {
  form_data: object;
};

export type CreateMyOnboardingSubmissionResponseBody = {
  onboarding_submission: OnboardingSubmission;
  team: Team;
};

export type GetMyOnboardingSubmissionResponseBody = {
  onboarding_submission: OnboardingSubmission;
  team: Team;
};

export type Team = {
  id: string;
  name: string;
  dashboard_access: number;
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
  dashboard_access?: number;
  onboardingSubmission?: object; // opaque type for now since we currently only care if value is set
  virtualEvents?: VirtualEventDetails[];
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

// The additional properties are set in the template header, so we know they exist.
export const eaveWindow: GlobalEaveWindow = window as GlobalEaveWindow;
