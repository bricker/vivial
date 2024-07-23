import React from "react";
import { makeStyles } from "tss-react/mui";

const useStyles = makeStyles()((theme) => ({}));

export default function SetupStep() {
  const { classes } = useStyles();

  return (
    <div>
      <h1> Testing</h1>
    </div>
  );
}
