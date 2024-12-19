import ExternalLink from "$eave-dashboard/js/components/Links/ExternalLink";
import { Activity, AdminBookingInfo } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";

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
  // TODO: edit
  return (
    <div>
      <h2>Activity info</h2>
      <h3>Core internal details:</h3>
      {data ? (
        <div>
          <b>Name: {data.activityName}</b>
          <p>at time: {data.activityStartTime}</p>
          <p>
            Website/booking link:{" "}
            {data.activityBookingLink ? (
              <ExternalLink to={data.activityBookingLink}>{data.activityBookingLink}</ExternalLink>
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
      <h3>Extra details:</h3>
      {detailData ? (
        <div>
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
