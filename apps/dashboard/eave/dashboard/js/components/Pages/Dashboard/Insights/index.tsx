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

const Insights = () => {
  const { classes } = makeClasses();

  return <iframe src={`${eaveWindow.eavedash.embedBase}/auth/sso`} className={classes.embedding}></iframe>;
};

export default Insights;
