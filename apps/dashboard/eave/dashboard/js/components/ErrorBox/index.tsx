import { Typography } from "@mui/material";
import React from "react";
import { makeStyles } from "tss-react/mui";
import ErrorIcon from "../Icons/ErrorIcon";

const makeClasses = makeStyles()((theme) => ({
  errorBox: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
    gap: 16,
    width: "100%",
    padding: 16,
    backgroundColor: "#ff38380d",
    color: "#AD0000",
    marginBottom: 15,
    border: "1px solid #ff383840",
    borderRadius: 8,
  },
}));

const ErrorBox = ({ children }: { children: React.ReactNode }) => {
  const { classes } = makeClasses();

  return (
    <div className={classes.errorBox}>
      <ErrorIcon color="#AD0000" />
      <Typography variant="subtitle1">{children}</Typography>
    </div>
  );
};

export default ErrorBox;
