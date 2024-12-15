import { styled } from "@mui/material";
import React, { useEffect, useState } from "react";

import { useGetOutingPreferencesQuery, useGetOutingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { chosePreferences, plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";

import ActivitySection from "./Sections/ActivitySection";
import BookingSection from "./Sections/BookingSection";
import DistanceSection from "./Sections/DistanceSection";
import LogisticsSection from "./Sections/LogisticsSection";
import RestaurantSection from "./Sections/RestaurantSection";
import LoadingView from "./Views/LoadingView";

const PageContainer = styled("div")(() => ({
  paddingBottom: 102,
}));

const DateItineraryPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const outingId = params["outingId"] || "";
  const outing = useSelector((state: RootState) => state.outing.details);
  const [skipQueries, setSkipQueries] = useState(true);
  const { data: preferencesData, isLoading: preferencesLoading } = useGetOutingPreferencesQuery(
    {},
    { skip: skipQueries },
  );
  const { data: outingData, isLoading: outingDataLoading } = useGetOutingQuery(
    { input: { id: outingId } },
    { skip: skipQueries },
  );

  useEffect(() => {
    if (outing === null) {
      setSkipQueries(false);
    }
  }, [outing]);

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

  if (!outing || outingDataLoading || preferencesLoading) {
    return <LoadingView />;
  }

  return (
    <PageContainer>
      <LogisticsSection />
      <BookingSection />
      <RestaurantSection />
      <DistanceSection />
      <ActivitySection />
    </PageContainer>
  );
};

export default DateItineraryPage;
