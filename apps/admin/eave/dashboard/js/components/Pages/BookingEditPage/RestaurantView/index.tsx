import { AdminBookingInfo, Restaurant } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";
import { Link } from "react-router-dom";

const RestaurantView = ({
  data,
  detailData,
  isLoading,
}: {
  data: AdminBookingInfo | undefined | null;
  detailData: Restaurant | undefined | null;
  isLoading: boolean;
}) => {
  const fallback = "[none]";
  return (
    <div>
      <h2>Restaurant info</h2>
      {data ? (
        <div>
          <h3>Core internal info</h3>
          <b>Name: {data.restaurantName}</b>
          <p>at time: {data.restaurantArrivalTime}</p>
          <p>
            Reserve at:{" "}
            {data.restaurantBookingLink ? (
              <Link to={data.restaurantBookingLink}>{data.restaurantBookingLink}</Link>
            ) : (
              "[no booking URL]"
            )}{" "}
          </p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
      {detailData ? (
        <div>
          <h3>Extra details:</h3>
          {/* <p>{detailData.description}</p> */}
          {detailData.reservable && <b>Reservation possible; Please reserve.</b>}
          <p>
            Source: {detailData.source}
            ID: {detailData.sourceId}
          </p>
          <p>
            Location:
            {detailData.location.address.formattedMultiline}
          </p>
          <p>{`(in region: ${detailData.location.searchRegion.name})`}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </div>
  );
};

export default RestaurantView;
