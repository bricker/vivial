import { useGetOutingQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import React, { useEffect, useState } from "react";

import { useDispatch, useSelector } from "react-redux";
import { useParams } from "react-router-dom";

import { RootState } from "$eave-dashboard/js/store";
import { plannedOuting } from "$eave-dashboard/js/store/slices/outingSlice";

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
  const [skipOutingQuery, setSkipOutingQuery] = useState(true);
  const { data: outingData, isLoading: outingDataLoading } = useGetOutingQuery(
    { input: { id: outingId } },
    { skip: skipOutingQuery },
  );

  useEffect(() => {
    if (outing === null) {
      setSkipOutingQuery(false);
    }
  }, [outing]);

  useEffect(() => {
    if (outingData?.outing) {
      dispatch(plannedOuting({ outing: outingData.outing }));
    }
  }, [outingData]);

  if (!outing || outingDataLoading) {
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
