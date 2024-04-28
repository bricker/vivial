import { eaveWindow } from "$eave-dashboard/js/types";
import React from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  embedding: {
    width: "100%",
    height: "100%",
    border: "none",
  },
}));

const Insights = ({ dashRoute = undefined }: { dashRoute?: string }) => {
  const { classes } = makeClasses();

  let qp = "";
  if (dashRoute) {
    qp += `return_to=${dashRoute}`;
  }
  return (
    <iframe
      src={`${eaveWindow.eave.apiBase}/oauth/metabase?${qp}`}
      className={classes.embedding}
    ></iframe>
  );
};

export default Insights;
