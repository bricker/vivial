import { AdminUpdateBookingFailureReason, BookingState } from "$eave-dashboard/js/graphql/generated/graphql";
import { useGetBookingInfoQuery, useUpdateBookingMutation } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { styled } from "@mui/material";
import React, { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import LoadingButton from "../../Buttons/LoadingButton";
import ActivityView from "./ActivityView";
import CostBreakdownView from "./CostBreakdownView";
import ReserverDetailsView from "./ReserverDetailsView";
import RestaurantView from "./RestaurantView";
import SurveyView from "./SurveyView";

const PageContainer = styled("div")(() => ({
  padding: 24,
}));

const BookingEditPage = () => {
  const [error, setError] = useState("");
  const params = useParams();
  const bookingId = params["bookingId"];
  if (!bookingId) {
    return <h1 style={{ color: "red" }}>Booking ID is required. please add it as a path parameter</h1>;
  }
  const { data: bookingInfo, isLoading: bookingIsLoading } = useGetBookingInfoQuery({ bookingId });
  const [updateBooking, { isLoading: updateBookingIsLoading }] = useUpdateBookingMutation();

  const setBookingState = async ({ bookingId, state }: { bookingId: string; state: BookingState }) => {
    setError("");

    const resp = await updateBooking({
      input: { bookingId, state },
    });

    switch (resp.data?.adminUpdateBooking?.__typename) {
      case "AdminUpdateBookingSuccess": {
        // yay we done it
        break;
      }
      case "AdminUpdateBookingFailure": {
        switch (resp.data.adminUpdateBooking.failureReason) {
          case AdminUpdateBookingFailureReason.ActivitySourceNotFound:
            setError("New activity indicated by source + source ID was not found");
            break;
          case AdminUpdateBookingFailureReason.BookingNotFound:
            setError("The booking can no longer be found");
            break;
          case AdminUpdateBookingFailureReason.ValidationErrors:
            setError(
              `Validation failed for following: ${resp.data.adminUpdateBooking.validationErrors
                ?.map((e) => e.field)
                .join(", ")}`,
            );
            break;
          default:
            setError(`unhandled AdminUpdateBookingFailureReason: ${resp.data.adminUpdateBooking.failureReason}`);
            break;
        }
        break;
      }
      default:
        // some kind of error?
        if (resp.error) {
          setError(JSON.stringify(resp.error));
        }
    }
  };

  const handleBookBooking = useCallback(async () => {
    await setBookingState({ bookingId, state: BookingState.Booked });
  }, []);

  const handleCancelBooking = useCallback(async () => {
    await setBookingState({ bookingId, state: BookingState.Canceled });
  }, []);

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

        <div style={{ display: "flex", justifyContent: "space-around" }}>
          <LoadingButton color="secondary" loading={updateBookingIsLoading} onClick={handleCancelBooking}>
            Cancel Booking
          </LoadingButton>
          <LoadingButton loading={updateBookingIsLoading} onClick={handleBookBooking}>
            Mark as Booked
          </LoadingButton>
        </div>
      </div>
      {!bookingIsLoading && !bookingInfo?.adminBooking && (
        <h2 style={{ color: "red" }}>ERROR: failed to get booking</h2>
      )}
      {error && <h2 style={{ color: "red" }}>ERROR: {error}</h2>}
    </PageContainer>
  );
};

export default BookingEditPage;
