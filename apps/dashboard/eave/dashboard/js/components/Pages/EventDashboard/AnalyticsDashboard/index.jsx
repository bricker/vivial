// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars
import MetabaseEmbeddedDashboard from "../../../MetabaseEmbeddedDashboard/index.jsx";

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  embedding: {
    width: "100%",
    height: "100%",
    border: "none",
  },
}));

const AnalyticsDashboard = () => {
  const classes = makeClasses();

  return <MetabaseEmbeddedDashboard className={classes.embedding} />;
};

export default AnalyticsDashboard;
