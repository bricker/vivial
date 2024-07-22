"use client";
import React from "react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()(() => ({
  main: {
    display: "flex",
    height: "100vh",
    overflow: "hidden",
  },
}));

const Waitlist = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.main}>
      <h1> Waitlist </h1>
    </div>
  );
};

export default Waitlist;
