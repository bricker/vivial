import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import { AdminBookingInfo, Restaurant } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";

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
      <h3>Core internal details:</h3>
      {data ? (
        <div>
          <b>Name: {data.restaurantName}</b>
          <p>at time: {data.restaurantArrivalTime}</p>
          <p>
            Reserve at:{" "}
            {data.restaurantBookingLink ? (
              <ExternalLink to={data.restaurantBookingLink}>{data.restaurantBookingLink}</ExternalLink>
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
      <h3>Extra details:</h3>
      {detailData ? (
        <div>
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
