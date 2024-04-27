// @ts-check
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../../types.js"; // eslint-disable-line no-unused-vars

const makeClasses = makeStyles((/** @type {Types.Theme} */ _theme) => ({
  embedding: {
    width: "100%",
    height: "100%",
    border: "none",
  },
}));

const Insights = (
  /** @type {{dashRoute?: string}} */
  {
    dashRoute = undefined,
  }
) => {
  const classes = makeClasses();

    // route to web backend to add auth headers etc before redirecting to core api
  // https://www.metabase.com/docs/latest/embedding/interactive-embedding#showing-or-hiding-metabase-ui-components
  let srcRoute = "/embed/metabase";
  if (dashRoute) {
    srcRoute += `?return_to=${dashRoute}`;
  }
  return <iframe src={srcRoute} className={classes.embedding}></iframe>;
};

export default Insights;
