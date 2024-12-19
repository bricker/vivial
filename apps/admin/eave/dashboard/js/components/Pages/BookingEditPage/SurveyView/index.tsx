import { Survey } from "$eave-dashboard/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";

const SurveyView = ({ data, isLoading }: { data: Survey | undefined | null; isLoading: boolean }) => {
  return (
    <div>
      <h2>Survey details:</h2>
      {data ? (
        <div>
          <p>headcount: {data.headcount}</p>
          <p>budget: {data.budget}</p>
          <p>open to following regions: {data.searchRegions.map((r) => r.name).join(", ")}</p>
          <p>at time: {data.startTime}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        "[None]"
      )}
    </div>
  );
};

export default SurveyView;
