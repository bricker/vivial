import { AppContext, AppContextProps } from "$eave-dashboard/js/context/AppContext";
import React from "react";
import { createBooking } from "../graphql/hooks/createBooking";
import { replanOuting } from "../graphql/hooks/replanOuting";
import { submitReserverDetails } from "../graphql/hooks/submitReserverDetails";
import { submitSurvey } from "../graphql/hooks/submitSurvey";

const AppContextProvider = ({ children }: { children: React.ReactNode }) => {
  const ctx: AppContextProps = {
    ...submitSurvey(),
    ...submitReserverDetails(),
    ...createBooking(),
    ...replanOuting(),
  };

  return <AppContext.Provider value={ctx}>{children}</AppContext.Provider>;
};

export default AppContextProvider;
