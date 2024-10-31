import { AppContext, AppContextProps } from "$eave-dashboard/js/context/AppContext";
import React from "react";
import { createBooking } from "../graphql/createBooking";
import { replanOuting } from "../graphql/outing";
import { submitReserverDetails } from "../graphql/submitReserverDetails";
import { submitSurvey } from "../graphql/submitSurvey";

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
