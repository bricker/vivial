export type VirtualEvent = {
  id: string;
  readable_name: string;
  description?: string;
  fields?: string[];
};

export type VirtualEventQueryInput = {
  search_term: string;
};

export type GetVirtualEventsResponseBody = {
  virtual_events: Array<VirtualEvent>;
};

export type Team = {
  id: string;
  name: string;
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
  virtualEvents?: VirtualEvent[];
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

// The additional properties are set in the template header, so we know they exist.
export const eaveWindow: GlobalEaveWindow = window as GlobalEaveWindow;
