import { AppContext, AppContextProps } from "$eave-dashboard/js/context/AppContext";
import React from "react";
import { submitReserverDetails } from "../graphql/submitReserverDetails";
import { submitSurvey } from "../graphql/submitSurvey";

const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const ctx: AppContextProps = {
    ...submitSurvey(),
    ...submitReserverDetails(),
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
