import { CircularProgress } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import React from "react";
import Page from "../Page/index.jsx";

const makeClasses = makeStyles((theme) => ({
  loader: {
    color: theme.palette.background.contrastText,
    width: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
}));

const LoadingPage = () => {
  const classes = makeClasses();
  return (
    <Page>
      <div className={classes.loader}>
        <CircularProgress color="inherit" />
      </div>
    </Page>
  );
};

export default LoadingPage;
