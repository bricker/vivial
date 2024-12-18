import { useGetBookingDetialsQuery } from "$eave-dashboard/js/store/slices/coreApiSlice";
import { CircularProgress } from "@mui/material";
import React from "react";
import { useParams } from "react-router-dom";

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
      {bookingInfo ? (
        <div>
          <h2>Reserver info:</h2>
          <div>
            <p>account id: todo</p>
            <p>First name: todo</p>
            <p>Last name: todo</p>
          </div>

          <h2>Activity info:</h2>
          <div>
            
          </div>

          <h2>Restaurant info:</h2>
          <div></div>

          <h2>Payment info:</h2>
          <div>
            <p>
              Stripe link: <a href="#">todo payment id</a>
            </p>
          </div>
        </div>
      ) : (
        <CircularProgress />
      )}
    </div>
  );
};

export default BookingEditPage;
