// @ts-check
import { Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import * as Types from "../../../types.js"; // eslint-disable-line no-unused-vars

const makeClasses = makeStyles((/** @type {Types.Theme} */ theme) => ({
  title: {
    fontSize: 28,
    fontWeight: 400,
    [theme.breakpoints.up("sm")]: {
      fontSize: 36,
    },
  },
}));

const UninstalledGithubAppDash = () => {
  const classes = makeClasses();

  return (
    <>
      <Typography className={classes.title}>
        Welcome to Better Documentation
      </Typography>
    </>
  );
};

export default UninstalledGithubAppDash;
