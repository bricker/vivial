import { useGetBookingDetialsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { CircularProgress } from "@mui/material";
import React from "react";
import { Link, useParams } from "react-router-dom";

const currencyFormatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
});

function formatCents(cents: number): string {
  return currencyFormatter.format(cents / 100);
}

const BookingEditPage = () => {
  const params = useParams();
  const bookingId = params["bookingId"];
  if (!bookingId) {
    return <h1 style={{ color: "red" }}>Booking ID is required. please add it as a path parameter</h1>;
  }
  const { data: bookingInfo, isLoading } = useGetBookingDetialsQuery({ input: { bookingId } });
  return (
    <div>
      <h1>Booking {bookingId}</h1>
      {bookingInfo?.adminBooking ? (
        <div>
          <h2>Reserver info:</h2>
          <div>
            <p>account id: todo</p>
            <p>First name: todo</p>
            <p>Last name: todo</p>
          </div>

          <h2>Activity info:</h2>
          <div>
            {bookingInfo.adminBooking.activity ? (
              <div>
                <h4>{bookingInfo.adminBooking.activity.name}</h4>
                <p>
                  Description:
                  {bookingInfo.adminBooking.activity.description}
                </p>
                <p>at time: {bookingInfo.adminBooking.activityStartTime}</p>
                <p>
                  Website link:{" "}
                  {bookingInfo.adminBooking.activity.websiteUri ? (
                    <Link to={bookingInfo.adminBooking.activity.websiteUri}>
                      {bookingInfo.adminBooking.activity.websiteUri}
                    </Link>
                  ) : (
                    "[none]"
                  )}
                </p>
                <p>
                  Source: {bookingInfo.adminBooking.activity.source} -- {bookingInfo.adminBooking.activity.sourceId}
                </p>
                <p>
                  Location: {bookingInfo.adminBooking.activity.venue.name}
                  {bookingInfo.adminBooking.activity.venue.location.address.formattedMultiline}
                </p>
                <p>{`(in region: ${bookingInfo.adminBooking.activity.venue.location.searchRegion.name})`}</p>
                <p>Category: {bookingInfo.adminBooking.activity.categoryGroup?.name}</p>
              </div>
            ) : (
              "[None]"
            )}
          </div>

          <h2>Restaurant info:</h2>
          <div>
            {bookingInfo.adminBooking.restaurant ? (
              <div>
                <h4>{bookingInfo.adminBooking.restaurant.name}</h4>
                <p>{bookingInfo.adminBooking.restaurant.description}</p>
                <p>at time: {bookingInfo.adminBooking.restaurantArrivalTime}</p>
                {bookingInfo.adminBooking.restaurant.reservable && (
                  <p>
                    Please reserve.{" "}
                    {bookingInfo.adminBooking.restaurant.websiteUri ? (
                      <Link to={bookingInfo.adminBooking.restaurant.websiteUri}>
                        {bookingInfo.adminBooking.restaurant.websiteUri}
                      </Link>
                    ) : (
                      "[no site URL]"
                    )}
                  </p>
                )}
                <p>
                  Source: {bookingInfo.adminBooking.restaurant.source} -- {bookingInfo.adminBooking.restaurant.sourceId}
                </p>
                <p>
                  Location:
                  {bookingInfo.adminBooking.restaurant.location.address.formattedMultiline}
                </p>
                <p>{`(in region: ${bookingInfo.adminBooking.restaurant.location.searchRegion.name})`}</p>
              </div>
            ) : (
              "[None]"
            )}
          </div>

          <h2>Cost info:</h2>
          <div>
            <h3>Cost breakdown</h3>
            <div>
              <p>Event costs: {formatCents(bookingInfo.adminBooking.costBreakdown.baseCostCents)}</p>
              <p>Taxes: {formatCents(bookingInfo.adminBooking.costBreakdown.taxCents)}</p>
              <p>Fees: {formatCents(bookingInfo.adminBooking.costBreakdown.feeCents)}</p>
              <p style={{ fontWeight: "bold" }}>{formatCents(bookingInfo.adminBooking.costBreakdown.totalCostCents)}</p>
            </div>
            <p>
              Stripe link: <Link to={"#"}>todo</Link>
            </p>
          </div>
        </div>
      ) : bookingInfo ? (
        <h2 style={{ color: "red" }}>Booking not found</h2>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        <h2 style={{ color: "red" }}>ERROR: failed to get booking</h2>
      )}
    </div>
  );
};

export default BookingEditPage;
