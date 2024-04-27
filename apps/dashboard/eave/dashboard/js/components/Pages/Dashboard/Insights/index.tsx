import React from "react";
import { makeStyles } from "tss-react/mui";

const makeClasses = makeStyles()(() => ({
  embedding: {
    width: "100%",
    height: "100%",
    border: "none",
  },
}));

const Insights = (
  { dashRoute = undefined }: { dashRoute?: string }
) => {
  const { classes } = makeClasses();

    // route to web backend to add auth headers etc before redirecting to core api
  // https://www.metabase.com/docs/latest/embedding/interactive-embedding#showing-or-hiding-metabase-ui-components
  let srcRoute = "/embed/metabase";
  if (dashRoute) {
    srcRoute += `?return_to=${dashRoute}`;
  }
  return <iframe src={srcRoute} className={classes.embedding}></iframe>;
};

export default Insights;
