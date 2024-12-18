import React from "react";
import { useSelector } from "react-redux";
import { useLocation } from "react-router-dom";

import { ITINERARY_PREFIX } from "$eave-dashboard/js/routes";
import { type RootState } from "$eave-dashboard/js/store";
import { isDesktop, useBreakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";

import ItineraryVariant from "./Variants/ItineraryVariant";
import LoggedInVariant, { DeviceType } from "./Variants/LoggedInVariant";
import LoggedOutVariant from "./Variants/LoggedOutVariant";

const GlobalHeader = () => {
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  const breakpoint = useBreakpoint();
  const { pathname } = useLocation();
  const isItinerary = pathname.startsWith(ITINERARY_PREFIX);

  if (isLoggedIn) {
    if (isDesktop(breakpoint)) {
      return <LoggedInVariant deviceType={DeviceType.Desktop} />;
    }
    return <LoggedInVariant deviceType={DeviceType.Mobile} />;
  }
  if (isItinerary) {
    return <ItineraryVariant />;
  }
  return <LoggedOutVariant />;
};

export default GlobalHeader;
