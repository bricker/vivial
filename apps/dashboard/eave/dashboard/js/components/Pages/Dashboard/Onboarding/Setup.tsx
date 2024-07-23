"use client";
import React from "react";
import { makeStyles } from "tss-react/mui";
import SetupStep from "./SetupStep";
const useStyles = makeStyles()(() => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
}));

const Setup = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.main}>
      <SetupStep />
    </div>
  );
};

export default Setup;
