import { Activity, AdminBookingInfo } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";
import { Link } from "react-router-dom";

const ActivityView = ({
  data,
  detailData,
  isLoading,
}: {
  data: AdminBookingInfo | undefined | null;
  detailData: Activity | undefined | null;
  isLoading: boolean;
}) => {
  const fallback = "[None]";
  // TODO: 
  return (
    <div>
      <h2>Activity info</h2>
      {data ? (
        <div>
          <h3>Core internal details:</h3>
          <b>Name: {data.activityName}</b>
          <p>at time: {data.activityStartTime}</p>
          <p>
            Website/booking link:{" "}
            {data.activityBookingLink ? (
              <Link to={data.activityBookingLink}>{data.activityBookingLink}</Link>
            ) : (
              fallback
            )}
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
          {/* <p>
            Description:
            {detailData.description}
          </p> */}
          <p>
            Source: {detailData.source}
            ID: {detailData.sourceId}
          </p>
          <p>
            Location: {detailData.venue.name}
            {detailData.venue.location.address.formattedMultiline}
          </p>
          <p>{`(in region: ${detailData.venue.location.searchRegion.name})`}</p>
          <p>Category: {detailData.categoryGroup?.name}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        fallback
      )}
    </div>
  );
};

export default ActivityView;
