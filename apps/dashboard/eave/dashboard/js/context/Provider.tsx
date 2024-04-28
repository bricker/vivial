import React, { createContext, useState } from "react";
import {
  DashboardNetworkState,
  DashboardTeam,
  GlossaryNetworkState,
} from "$eave-dashboard/js/types";

export type AppContextProps = {
  teamCtx?: [
    DashboardTeam | null,
    React.Dispatch<React.SetStateAction<DashboardTeam | null>>,
  ];
  dashboardNetworkStateCtx?: [
    DashboardNetworkState,
    React.Dispatch<React.SetStateAction<DashboardNetworkState>>,
  ];
  glossaryNetworkStateCtx?: [
    GlossaryNetworkState,
    React.Dispatch<React.SetStateAction<GlossaryNetworkState>>,
  ];
};

export const AppContext = createContext<AppContextProps>({});

const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const teamCtx = useState<DashboardTeam | null>(null);

  const dashboardNetworkStateCtx = useState<DashboardNetworkState>({
    teamIsLoading: true,
    teamIsErroring: false,
    teamRequestHasSucceededAtLeastOnce: false,
  });

  const glossaryNetworkStateCtx = useState<GlossaryNetworkState>({
    virtualEventsAreErroring: false,
    virtualEventsAreLoading: true,
  });

  const ctx: AppContextProps = {
    teamCtx,
    dashboardNetworkStateCtx,
    glossaryNetworkStateCtx,
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
