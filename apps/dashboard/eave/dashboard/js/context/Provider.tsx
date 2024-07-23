import { DashboardNetworkState, DashboardTeam, GlossaryNetworkState, OnboardingFormNetworkState } from "$eave-dashboard/js/types";
import React, { createContext, useState } from "react";

export type AppContextProps = {
  teamCtx?: [DashboardTeam | null, React.Dispatch<React.SetStateAction<DashboardTeam | null>>];
  dashboardNetworkStateCtx?: [DashboardNetworkState, React.Dispatch<React.SetStateAction<DashboardNetworkState>>];
  glossaryNetworkStateCtx?: [GlossaryNetworkState, React.Dispatch<React.SetStateAction<GlossaryNetworkState>>];
  onboardingFormNetworkStateCtx?: [OnboardingFormNetworkState, React.Dispatch<React.SetStateAction<OnboardingFormNetworkState>>];
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

  const onboardingFormNetworkStateCtx = useState<OnboardingFormNetworkState>({
    formSubmitIsErroring: false,
    formSubmitIsLoading: false,
    formDataIsLoading: true,
    formDataIsErroring: false,
  })

  const ctx: AppContextProps = {
    teamCtx,
    dashboardNetworkStateCtx,
    glossaryNetworkStateCtx,
    onboardingFormNetworkStateCtx,
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
