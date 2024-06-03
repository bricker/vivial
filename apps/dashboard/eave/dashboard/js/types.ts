export type VirtualEventField = {
  name: string;
  description?: string | null;
  field_type: string;
  mode: string | null;
  fields: VirtualEventField[] | null;
};

export type VirtualEventPeek = {
  id: string;
  view_id: string;
  readable_name: string;
  description?: string;
};

export type VirtualEventDetails = {
  id: string;
  view_id: string;
  readable_name: string;
  description?: string | null;
  fields: VirtualEventField[] | null;
};

export type ListMyVirtualEventsResponseBody = {
  virtual_events: Array<VirtualEventPeek>;
};

export type GetMyVirtualEventDetailsResponseBody = {
  virtual_events: Array<VirtualEventPeek>;
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
  virtualEvents?: VirtualEventPeek[];
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
