import { AppContext, AppContextProps } from "$eave-dashboard/js/context/AppContext";
import React from "react";
import { submitSurvey } from "../graphql/survey";

const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const ctx: AppContextProps = {
    ...submitSurvey,
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
