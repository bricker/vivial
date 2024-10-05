import React, { createContext, useState } from "react";

export type AppContextProps = {
};

export const AppContext = createContext<AppContextProps>({});

const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  // const dashboardNetworkStateCtx = useState<DashboardNetworkState>({
  //   teamIsLoading: true,
  //   teamIsErroring: false,
  //   teamRequestHasSucceededAtLeastOnce: false,
  // });


  const ctx: AppContextProps = {
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
