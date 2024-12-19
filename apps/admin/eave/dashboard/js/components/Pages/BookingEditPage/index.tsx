import { ActivitySource, RestaurantSource } from "$eave-dashboard/js/graphql/generated/graphql";
import { useGetBookingInfoQuery, useUpdateBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import ActivityView from "./ActivityView";
import CostBreakdownView from "./CostBreakdownView";
import ReserverDetailsView from "./ReserverDetailsView";
import RestaurantView from "./RestaurantView";
import SurveyView from "./SurveyView";

const PageContainer = styled("div")(() => ({
  padding: 24,
}));

const BookingEditPage = () => {
  const [newActivitySource, setNewActivitySource] = useState<ActivitySource | null | undefined>(undefined);
  const [newRestaurantSource, setNewRestaurantSource] = useState<RestaurantSource | null | undefined>(undefined);
  const [newActivitySourceId, setNewActivitySourceId] = useState<string | null | undefined>(undefined);
  const [newRestaurantSourceId, setNewRestaurantSourceId] = useState<string | null | undefined>(undefined);
  const [newActivityStartTime, setNewActivityStartTime] = useState<Date | null | undefined>(undefined);
  const [newRestaurantStartTime, setNewRestaurantStartTime] = useState<Date | null | undefined>(undefined);
  const [newActivityHeadcount, setNewActivityHeadcount] = useState<number | undefined>(undefined);
  const [newRestaurantHeadcount, setNewRestaurantHeadcount] = useState<number | undefined>(undefined);
  const params = useParams();
  const bookingId = params["bookingId"];
  if (!bookingId) {
    return <h1 style={{ color: "red" }}>Booking ID is required. please add it as a path parameter</h1>;
  }
  const { data: bookingInfo, isLoading: bookingIsLoading } = useGetBookingInfoQuery({ bookingId });
  const [updateBooking, { isLoading: updateBookingIsLoading }] = useUpdateBookingMutation();

  const handleUpdateBooking = useCallback(() => {
    updateBooking({
      input: {
        bookingId,
        activitySource: newActivitySource,
        activitySourceId: newActivitySourceId,
        restaurantSource: newRestaurantSource,
        restaurantSourceId: newRestaurantSourceId,
        activityStartTimeUtc: newActivityStartTime?.toUTCString(),
        restaurantStartTimeUtc: newRestaurantStartTime?.toUTCString(),
        activityHeadcount: newActivityHeadcount,
        restaurantHeadcount: newRestaurantHeadcount,
      },
    });
  }, [
    newActivitySource,
    newRestaurantSource,
    newActivitySourceId,
    newRestaurantSourceId,
    newRestaurantStartTime,
    newActivityStartTime,
    newActivityHeadcount,
    newRestaurantHeadcount,
  ]);

  // TODO: ability to update/delete aspects of booking
  return (
    <PageContainer>
      <h1>Booking {bookingId}</h1>
      <div>
        <ReserverDetailsView data={bookingInfo?.adminBooking} isLoading={bookingIsLoading} />

        <SurveyView data={bookingInfo?.adminBooking?.survey} isLoading={bookingIsLoading} />

        <RestaurantView
          data={bookingInfo?.adminBooking}
          detailData={bookingInfo?.adminBookingRestaurantDetail}
          isLoading={bookingIsLoading}
        />

        <ActivityView
          data={bookingInfo?.adminBooking}
          detailData={bookingInfo?.adminBookingActivityDetail}
          isLoading={bookingIsLoading}
        />

        <CostBreakdownView
          data={bookingInfo?.adminBookingActivityDetail?.ticketInfo?.costBreakdown}
          stripePaymentIntentId={bookingInfo?.adminBooking?.stripePaymentId}
          bookingState={bookingInfo?.adminBooking?.state}
          isLoading={bookingIsLoading}
        />

        {/* <LoadingButton loading={updateBookingIsLoading} onClick={handleUpdateBooking}>
            Update Booking
          </LoadingButton> */}
      </div>
      {!bookingIsLoading && !bookingInfo?.adminBooking && <h2 style={{ color: "red" }}>ERROR: failed to get booking</h2>}
    </PageContainer>
  );
};

export default BookingEditPage;
