import Paper from "$eave-admin/js/components/Paper";
import { Survey } from "$eave-admin/js/graphql/generated/graphql";
import { CircularProgress } from "@mui/material";
import React from "react";
import { formatDate } from "../helper";

const SurveyView = ({ data, isLoading }: { data: Survey | undefined | null; isLoading: boolean }) => {
  return (
    <Paper>
      <h2>Survey details:</h2>
      {data ? (
        <div>
          <p>headcount: {data.headcount}</p>
          <p>budget: {data.budget}</p>
          <p>open to following regions: {data.searchRegions.map((r) => r.name).join(", ")}</p>
          <p>at time: {formatDate(data.startTime)}</p>
        </div>
      ) : isLoading ? (
        <CircularProgress />
      ) : (
        "[None]"
      )}
    </Paper>
  );
};

export default SurveyView;
