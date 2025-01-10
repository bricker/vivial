import { styled } from "@mui/material";
import React, { useEffect } from "react";

import { useGetOutingPreferencesQuery, useGetOutingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { chosePreferences, plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";
import { Breakpoint } from "$eave-dashboard/js/theme/helpers/breakpoint";

import ActivitySection from "./Sections/ActivitySection";
import BookingSection from "./Sections/BookingSection";
import DistanceSection from "./Sections/DistanceSection";
import LogisticsSection from "./Sections/LogisticsSection";
import RestaurantSection from "./Sections/RestaurantSection";
import LoadingView from "./Views/LoadingView";
import PreferencesBanner from "./Views/PreferencesBanner";

export const PageContainer = styled("div")(({ theme }) => ({
  paddingBottom: 56,
  maxWidth: 600,
  [theme.breakpoints.up(Breakpoint.Medium)]: {
    border: `1.5px solid ${theme.palette.primary.main}`,
    borderRadius: 25,
    overflow: "hidden",
    margin: "56px auto",
    paddingBottom: 0,
  },
}));

const DateItineraryPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const outingId = params["outingId"] || "";
  const outing = useSelector((state: RootState) => state.outing.details);
  const isLoggedIn = useSelector((state: RootState) => state.auth.isLoggedIn);
  // run network queries if there's no cached `outing`, or the
  // cached `outing` is not the one requested by query params
  const skipQueries = outing?.id === outingId;
  const { data: preferencesData, isLoading: preferencesLoading } = useGetOutingPreferencesQuery(
    {},
    { skip: !isLoggedIn || skipQueries },
  );
  const { data: outingData, isFetching: outingDataLoading } = useGetOutingQuery(
    { input: { id: outingId } },
    { skip: skipQueries },
  );

  useEffect(() => {
    if (outingData?.outing) {
      dispatch(plannedOuting({ outing: outingData.outing }));
    }
  }, [outingData]);

  useEffect(() => {
    const viewer = preferencesData?.viewer;
    if (viewer?.__typename === "AuthenticatedViewerQueries") {
      dispatch(chosePreferences({ user: viewer.outingPreferences }));
    }
  }, [preferencesData]);

  if (outingDataLoading || preferencesLoading) {
    return <LoadingView />;
  }

  return (
    <PageContainer>
      <PreferencesBanner />
      <LogisticsSection />
      <RestaurantSection />
      <DistanceSection />
      <ActivitySection />
      <BookingSection />
    </PageContainer>
  );
};

export default DateItineraryPage;
