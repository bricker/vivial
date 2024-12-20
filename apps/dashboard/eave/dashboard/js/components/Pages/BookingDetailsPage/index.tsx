import { useGetBookingDetailsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { openedBookingDetails } from "$eave-dashboard/js/store/slices/outingSlice";
import React, { useEffect } from "react";
import { useDispatch } from "react-redux";
import { useParams } from "react-router-dom";

import { PageContainer } from "../DateItineraryPage";
import ActivitySection from "../DateItineraryPage/Sections/ActivitySection";
import BookingSection from "../DateItineraryPage/Sections/BookingSection";
import DistanceSection from "../DateItineraryPage/Sections/DistanceSection";
import LogisticsSection from "../DateItineraryPage/Sections/LogisticsSection";
import RestaurantSection from "../DateItineraryPage/Sections/RestaurantSection";
import LoadingView from "../DateItineraryPage/Views/LoadingView";

const BookingDetailsPage = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const bookingId = params["bookingId"]!;
  const { data, isLoading } = useGetBookingDetailsQuery({ input: { bookingId } });

  useEffect(() => {
    if (data?.viewer?.__typename === "AuthenticatedViewerQueries") {
      const bookingDetails = data.viewer.bookedOutingDetails;
      if (bookingDetails) {
        dispatch(openedBookingDetails({ bookingDetails }));
      }
    }
  }, [data]);

  if (isLoading) {
    return <LoadingView />;
  }

  return (
    <PageContainer>
      <LogisticsSection viewOnly />
      <RestaurantSection />
      <DistanceSection />
      <ActivitySection />
      <BookingSection viewOnly />
    </PageContainer>
  );
};

export default BookingDetailsPage;
