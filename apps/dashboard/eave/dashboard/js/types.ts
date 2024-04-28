import { VirtualEvent } from "@eave-fyi/eave-stdlib-ts/src/core-api/models/virtual-event.js";

export type GlobalEaveWindow = Window &
  typeof globalThis & {
    eave: {
      cookieDomain?: string;
      apiBase?: string;
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
